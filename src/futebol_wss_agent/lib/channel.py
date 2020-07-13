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

from six import PY3

from .utils import frequency_to_wavelength
from .verification import FrozenObject

if PY3:
    from collections.abc import Mapping
else:
    from collections import Mapping


class Channel(Mapping):
    """Data structure that represents a WDM channel.

    Attributes
    ----------
    central_frequency :  float
        Central frequency in THz.
    bandwidth : float
        Bandwidth in GHz.
    attenuation : float
        Attenuation in dB.
    blocked : bool
        Boolean value that defines if the channel is locked or not.
        Default: :obj:`False`.
    port : int
        Destination / origin port.
    """

    MUTABLE_PROPERTIES = ('attenuation', 'blocked', 'port')
    IMMUTABLE_PROPERTIES = ('central_frequency', 'bandwidth')

    _frozen = False

    def __init__(self, central_frequency, bandwidth,
                 attenuation=0, blocked=False, port=1):
        # namedtuple requires overriding __new__ insteadof __init__
        self._central_frequency = central_frequency
        self._bandwidth = bandwidth
        self.attenuation = attenuation
        self.blocked = blocked
        self.port = port

    @property
    def central_frequency(self):
        """Central frequency in THz."""
        return self._central_frequency

    @property
    def bandwidth(self):
        """Bandwidth in GHz."""
        return self._bandwidth

    @property
    def start_frequency(self):
        """Start frequency in THz."""
        return self.central_frequency - self.bandwidth/2e3

    @property
    def stop_frequency(self):
        """Stop frequency, values in THz."""
        return self.central_frequency + self.bandwidth/2e3

    @property
    def central_wavelength(self):
        """Central wavelength in nm."""
        return frequency_to_wavelength(self.central_frequency)

    @property
    def start_wavelength(self):
        """Start wavelength in nm."""
        return frequency_to_wavelength(self.stop_frequency)

    @property
    def stop_wavelength(self):
        """Start wavelength in nm."""
        return frequency_to_wavelength(self.start_frequency)

    def __repr__(self):
        return self.__class__.__name__ + '(' + ', '.join(
            ['{}={}'.format(k, getattr(self, '_'+k))
             for k in self.IMMUTABLE_PROPERTIES] +
            ['{}={}'.format(k, getattr(self, k))
             for k in self.MUTABLE_PROPERTIES]
        ) + ')'

    def __getstate__(self):
        state = {}
        state.update({
            k: getattr(self, '_'+k) for k in
            self.IMMUTABLE_PROPERTIES
        })
        state.update({k: getattr(self, k) for k in self.MUTABLE_PROPERTIES})

        return state

    def __setstate__(self, state):
        for k in self.IMMUTABLE_PROPERTIES:
            setattr(self, '_'+k, state[k])
        for k in self.MUTABLE_PROPERTIES:
            setattr(self, k, state[k])

    def __getitem__(self, key):
        return self.__getstate__()[key]

    def __iter__(self):
        return iter(self.__getstate__())

    def __len__(self):
        return len(self.__getstate__())

    def __setattr__(self, name, value):
        """\
        Intercepts all the property changes, denying them if object is frozen.
        """
        if self._frozen:
            raise FrozenObject
        else:
            super(Channel, self).__setattr__(name, value)

    def copy(self):
        """Copies the object.

        When a frozen object is copied the new object is fresh and mutable.
        """
        return self.__class__(self.central_frequency,
                              self.bandwidth,
                              self.attenuation,
                              self.blocked,
                              self.port)
    __copy__ = __deepcopy__ = copy

    def freeze(self):
        """Seal object, avoiding future changes."""
        self._frozen = True
        return self
