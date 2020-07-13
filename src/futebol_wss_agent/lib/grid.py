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

from itertools import repeat

from six import PY3, string_types
from six.moves import xrange as xrangex

from .channel import Channel
from .utils import wavelength_to_frequency
from .verification import ReadonlyAttribute

if PY3:
    from collections.abc import Sequence, Iterable
else:
    from collections import Sequence, Iterable

TOLERANCE = 1e-6


def _is_iterable(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, string_types)


class PropertyView(object):
    """Descriptor protocol to enable numpy.recarray-like interface.
    It means 2 things:

    - If you ``get`` a property from a collection, you will end up with another
      collection that enumerates the result of getting the same property
      for each item in the original collection. For example::

        collection.prop # => [item0.prop, item1.prop, ..., itemN.prop]

    - If you ``set`` a property in a collection, each item in this collection
      will have its equivalent property changed to the passed value. For
      example::

        collection.prop = scalar_value
        # Equivalent to:
        # item1.prop = scalar_value
        # item2.prop = scalar_valuei
        # ...
        # itemN.prop = scalar_value

        collection.prop = value_collection
        # Equivalent to:
        # item1.prop = value_collection[0]
        # item2.prop = value_collection[1]
        # ...
        # itemN.prop = value_collection[N]

    Usage
    -----

    .. code-block:: python

        class Collection(object):
            # Class that implements iterator protocol
            some_property = PropertyView('some_property')
            another_property = PropertyView('another_property', readonly=True)
            yet_another = PropertyView('may_have_different_target_name')

        class ObjectWithCollectionMember(object):
            # Class is not a collection but has a collection as attribute
            # called `iterable`
            iterable = []
            some_property = PropertyView('come_property', delegate='iterable')
    """

    def __init__(self, name, delegate=None, readonly=False):
        self.name = name
        self._readonly = readonly
        self.delegate = delegate

    def __get__(self, instance, _=None):
        if self.delegate is not None:
            collection = getattr(instance, self.delegate)
        else:
            collection = instance

        return [getattr(obj, self.name) for obj in collection]

    def __set__(self, instance, value):
        if self._readonly:
            raise ReadonlyAttribute

        if self.delegate is not None:
            collection = getattr(instance, self.delegate)
        else:
            collection = instance

        values = value if _is_iterable(value) else repeat(value)
        for obj, val in zip(collection, values):
            setattr(obj, self.name, val)


def add_property_views(cls):
    """Augment Grid with views to channel properties."""

    for attr in 'attenuation', 'blocked', 'port':
        setattr(cls, attr, PropertyView(attr))

    for attr in ('central_frequency', 'bandwidth',
                 'start_frequency', 'stop_frequency',
                 'central_wavelength', 'start_wavelength', 'stop_wavelength'):
        setattr(cls, attr, PropertyView(attr, readonly=True))

    return cls


@add_property_views
class Grid(Sequence):
    """Collection of channels that define a flex WDM grid."""

    def __init__(self, channels):
        self._channels = []

        for channel in channels:
            if not isinstance(channel, Channel):
                raise ValueError("Channels must be instances of the Channel"
                                 " class. `{}` give.".format(
                                     channel.__class__))
            self._channels.append(channel)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self._channels) + ')'

    def __len__(self):
        return len(self._channels)

    def __getitem__(self, index):
        """Retrieve an element or slice of the grid.

        It is possible to use this method as a regular list,
        but it can be also used to filter channels inside an specific frequency
        or wavelength range.

        Examples
        --------

            grid[0] # => Channel(...)
            grid[0:12] # => [Channel(...), ...Channel(...)]
            grid['frequency', 184.5:196.1] # => [Channel(...), ...Channel(...)]
            grid['wavelength', 1545:1560] # => [Channel(...), ...Channel(...)]
        """
        if isinstance(index, tuple):
            attr, index = index
            if not isinstance(index, slice):
                raise ValueError('When a attribute name is provided, '
                                 'the second parameter is expected to be a '
                                 'slice range. Value given: `{}`'.format(
                                     index))
            return self.filter(attr, index.start, index.stop, index.step)

        if isinstance(index, Iterable):
            item = [self._channels[i] for i in index]
        else:
            item = self._channels[index]

        if isinstance(item, Sequence):
            return Grid(item)

        return item

    def filter(self, attr, start=None, stop=None, step=None):
        """Filter the elements of the grid according to a specific frequency
        or wavelength range.

        Attributes
        ----------
        attr : str
            'frequency' or 'wavelength'.
        start : float
            Inferior boundary value.
        stop : float
            Superior boundary value.
        step : float
            Minimum delta between each element.

        Returns
        -------
            New collection of channels.
        """

        print('attr', attr)
        result = []
        last_value = None
        attr = 'frequency' if 'freq' in attr else 'wavelength'

        for channel in self._channels:
            if start and getattr(channel, 'start_{}'.format(attr)) < start:
                continue
            if stop and getattr(channel, 'stop_{}'.format(attr)) >= stop:
                continue

            current_value = getattr(channel, 'central_{}'.format(attr))

            if (last_value is None or step is None or
                    abs(current_value - last_value) >= (1-TOLERANCE)*step):
                result.append(channel)
                last_value = current_value

        return Grid(result)

    def copy(self):
        """Copies the grid.

        When a frozen grid is copied the new grid is fresh and mutable.
        """
        return self.__class__(c.copy() for c in self._channels)
    __copy__ = __deepcopy__ = copy

    def freeze(self):
        """Seal each channel, avoiding future changes."""

        for channel in self._channels:
            channel.freeze()

        return self


class FixedGrid(Grid):
    """Homogeneous collection of channels.

    Arguments
    ---------
    number : int
        Number of channels in the grid. By default 80.
    first_frequency : float
        Central frequency for the first channel, in THz.
        By default correspond to the C21 ITU channel.
    first_wavelength : float
        Central wavelength for the first channel, in nm.
        This argument overrides ``first_frequency``.
    bandwidth : float
        Channel width in GHz. 50 GHz by default.
    spacing : float
        Frequency spacing between consecutive channels in GHz. 0 by default.
    """

    DEFAULT_FIRST_FREQUENCY = 192.1
    """Default start point for grid, in THz."""

    DEFAULT_BANDWIDTH = 50
    """Default channel width in GHz."""

    DEFAULT_SPACING = 0
    """Default frequency leap between channels in GHz."""

    def __init__(self,
                 channels=None,
                 number=80,
                 first_frequency=DEFAULT_FIRST_FREQUENCY,
                 first_wavelength=None,
                 bandwidth=DEFAULT_BANDWIDTH,
                 spacing=DEFAULT_SPACING):

        if channels is None:
            if first_wavelength:
                first_frequency = wavelength_to_frequency(first_wavelength)

            freqs = (
                first_frequency + j*spacing*1e-3 + j*bandwidth*1e-3
                for j in xrangex(number)
            )

            channels = (Channel(f, bandwidth) for f in freqs)

        super(FixedGrid, self).__init__(channels)
