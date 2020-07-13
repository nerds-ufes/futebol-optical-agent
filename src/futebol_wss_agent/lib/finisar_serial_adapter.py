#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017-2022 Anderson Bravalheri, Univertity of Bristol
#                                       High Performance Networks Group
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import

import re
from math import floor
from time import sleep

from .channel import Channel
from .cli import MalformedResponse, Serial
from .verification import OutOfRange, OverlappedChannels, UnsupportedResolution

TOLERANCE = 1e-6


def is_grid_tainted(wss):
    """Determines if the grid must be rebuilt."""

    # No grid was set yet
    if wss.previous_state is None:
        return True

    delta = wss.changes()

    if any(k in delta for k in ('$insert', '$delete')):
        return True

    # Even if no channel was inserted or deleted, some channel may have
    # fundamental properties changed, and therefore the grid must be rebuilt
    return any(
        any(k in v.get('$update', {}) for k in Channel.IMMUTABLE_PROPERTIES)
        for v in delta.values()
    )


class _Communication(object):
    """Encapsulates communication with Finisar WSS via Serial.

    Note
    ----
    This class is unstable and not part of the main API, therefore should not
    be used.

    Arguments
    ---------
    interface : inclinations.Serial or None
        If no interface is passed, a new one will be created with the default
        options.
    use_checksum : bool
        If True, the wire protocol includes checksum.
    """

    def __init__(self, interface=None, use_checksum=True):
        self.use_checksum = use_checksum
        self.interface = interface if interface else Serial()
        self.interface.config.update(
            prompt_string='\^?OK(\$FF66)?',
            error_regex=re.compile(
                r'\^?(CER|AER|RER|VER)(\$[A-F0-9]{4})?\s*$', re.I),
            eol='\r\n'
        )
        # Make sure that no garbage is received from equipment
        sleep(1)
        self.interface.send_line('', flush=True)
        sleep(1)
        self.interface.flush()

    @staticmethod
    def checksum(command_str):
        """Finisar checksum is the 16-bit 2-complement of the sum of the bytes
        that correspond to each charater.
        """
        return (0xFFFF - sum(ord(ch) for ch in command_str)) + 0b1

    def verify_response_line(self, line):
        """True if line is well-formed, False otherwise."""
        line = line.strip()
        if not line:
            return True

        if line[0] != '^':
            return False

        content, checksum = line[1:].split('$')
        if not content or not checksum:
            return False

        if self.checksum(content) != int(checksum, 16):
            return False

    def verify_response_checksum(self, response):
        """Raises a :obj:`MalformedResponse` if response does not follow the
        correct wire protocol.
        """
        if any(self.verify_response_line(l) for l in response):
            raise MalformedResponse(
                "Response does not match the expected checksum:\n" + response)

    @staticmethod
    def strip_response_checksum(response):
        return response.strip()[1:].split("$")[0]

    def command(self, command_str):
        """Send the command using wire protocol that contains checksum."""
        #if self.use_checksum:
        #    cmd = "^{:s}${:04X}".format(
        #            command_str, self.checksum(command_str))
        #    response = self.interface.command(cmd)
        #    self.verify_response_checksum(response)
        #else:
        response = self.interface.command(command_str)

        return self.strip_response_checksum(response)

    def enforce_flexgrid(self):
        return self.command("CHW 0")

    def configure_grid(self, slices):
        """Configure WSS grid.

        Arguments
        ---------
        slices : list
            List of tuples, where each tuple has two elements, the first one
            is the number of the first spectral slice to be used and the
            second one is the number of the last spectral slice to be used
        """
        return self.command("DCC " + "".join(
            "{:d}={:d}:{:d};".format(i+1, s0, sf)
            for i, (s0, sf) in enumerate(slices)
        ))

    def update_grid(self, settings):
        """Update channels attenuation and port.

        Arguments
        ---------
        settings : list
            List of tuples, where each tuple has two elements, the first one
            is an integer corresponding to the routing port and the
            second one is the attenuation value in dB.
            If the channel is blocked, the tuple should be (99, 99.9).
        """
        return self.command("UCA " + "".join(
            "{:d},{:d},{:0.1f};".format(i+1, port, att)
            for i, (port, att) in enumerate(settings)
        ))


class Adapter(object):
    """Encapsulates Finisar WSS configuration.

    Keyword Arguments
    -----------------
    resolution : float
        Granularity of the slice width in GHz. Default 6.25.
    max_attenuation : float
        Attenuation range in dB. 15 dB by default.
    interface : inclinations.Abstract or None
        If no interface is passed, a new one (Serial) will be created with the
        default options.
    use_checksum : bool
        If True, the wire protocol includes checksum.
    frequency_window : tuple
        Spectral boundaries for channels. ``(191.325, 196.150)`` by default.
    """

    def __init__(self,
                 resolution=6.25,
                 max_attenuation=15,
                 interface=None,
                 use_checksum=True,
                 frequency_window=(191.325, 196.150)):

        self.frequency_window = frequency_window
        self.resolution = resolution
        self.max_attenuation = max_attenuation
        self._comm = _Communication(interface, use_checksum)

    def validate(self, wss):
        """Hook for validating WSS grid"""
        last_freq = None

        for channel in wss.grid:
            if abs(channel.bandwidth % self.resolution) > TOLERANCE:
                raise UnsupportedResolution(
                        "Finisar WSS only supports slices of {} GHz, "
                        "but bandwidth is {} GHz.".format(
                            self.resolution,
                            channel.bandwidth))

            # frequency delta should be multiple of resolution
            df = self.resolution*1e-3
            f = channel.start_frequency
            f0 = self.frequency_window[0]
            div = abs(f - f0)/df
            if TOLERANCE < abs(div - int(floor(div))) < 1 - TOLERANCE:
                # Modular algebra with floating point is very difficult due to
                # precision :(
                raise UnsupportedResolution(
                        "Finisar WSS resolution is {} GHz, "
                        "but spectral window starts at {} THz "
                        "and current channel starts at {} THz.".format(
                            self.resolution,
                            self.frequency_window[0],
                            channel.start_frequency))

            start_freq = channel.start_frequency
            if last_freq and start_freq < last_freq - TOLERANCE:
                raise OverlappedChannels("New channel starts at {}, but "
                                         "last channel stops at {}".format(
                                            start_freq, last_freq))
            last_freq = channel.stop_frequency

            if channel.attenuation > self.max_attenuation:
                raise OutOfRange("Finisar WSS attenuation is {} at maximum, "
                                 "{} is not supported.".format(
                                    self.max_attenuation,
                                    channel.attenuation))

            if channel.start_frequency < self.frequency_window[0]:
                raise OutOfRange("Finisar WSS frequency window is {}, but "
                                 "channel starts at: {}.".format(
                                     self.frequency_window,
                                     channel.start_frequency))

            if channel.stop_frequency > self.frequency_window[1]:
                raise OutOfRange("Finisar WSS frequency window is {}, but "
                                 "channel stops at: {}.".format(
                                     self.frequency_window,
                                     channel.stop_frequency))

            return True

    def _first_slice(self, channel):
        df = self.resolution*1e-3
        f = channel.start_frequency
        f0 = self.frequency_window[0]

        return int(round((f-f0) / df)) + 1  # starts at 1

    def _last_slice(self, channel):
        df = self.resolution*1e-3
        f = channel.stop_frequency
        f0 = self.frequency_window[0] + df

        return int(round((f-f0) / df)) + 1  # starts at 1

    @staticmethod
    def _port(channel):
        return 99 if channel.blocked else channel.port

    @staticmethod
    def _attenuation(channel):
        return 99.9 if channel.blocked else channel.attenuation

    def commit(self, wss):
        """Configure equipment with new settings."""

        if is_grid_tainted(wss):
            self._comm.enforce_flexgrid()
            self._comm.configure_grid(
                (self._first_slice(channel), self._last_slice(channel))
                for channel in wss.grid
            )

        self._comm.update_grid(
            (self._port(channel), self._attenuation(channel))
            for channel in wss.grid
        )
