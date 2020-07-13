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
"""Reusable functions related to common optical math."""

SPEED_OF_LIGHT = 299792458
"""Speed of light in vacuum."""


def wavelength_to_frequency_si(wavelength, speed_of_light=SPEED_OF_LIGHT):
    """Converts wavelength values to frequency.

    Arguments
    ---------
    wavelength : float
        Spatial period of the wave in meters.
    speed_of_light : float
        Value of the speed of the light for a certain medium in m/s.
        Defaults to the speed of light in vacuum (~ 3e8 m/s).

    Returns
    -------
    float
        Frequency value (inverse of temporal period) in Hz.
    """
    return speed_of_light / wavelength


def wavelength_to_frequency(wavelength, speed_of_light=SPEED_OF_LIGHT):
    """Similar to :obj:`wavelength_to_frequency_si` but uses nm and THz.

    See Also
    --------
        :obj:`wavelength_to_frequency_si`
    """
    return wavelength_to_frequency_si(wavelength * 1e-9, speed_of_light) / 1e12


def frequency_to_wavelength_si(frequency, speed_of_light=SPEED_OF_LIGHT):
    """Converts frequency values to wavelength.

    Arguments
    ---------
    frequency : float
        Inverse of the temporal period of the wave in Hertz.
    speed_of_light : float
        Value of the speed of the light for a certain medium in m/s.
        Defaults to the speed of light in vacuum (~ 3e8 m/s).

    Returns
    -------
    float
        Spatial period of the wave in meters.
    """
    return speed_of_light / frequency


def frequency_to_wavelength(frequency, speed_of_light=SPEED_OF_LIGHT):
    """Similar to :obj:`frequency_to_wavelength_si` but uses THz and nm.

    See Also
    --------

        * :obj:`wavelength_to_frequency_si`
    """
    return frequency_to_wavelength_si(frequency * 1e12, speed_of_light) / 1e-9
