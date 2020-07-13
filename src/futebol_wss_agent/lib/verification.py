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

class UndefinedAdapter(RuntimeWarning):
    """Avoid committing grid if adapter not specified."""

    DEFAULT_MESSAGE = "Please use a valid adapter when defining the grid."

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(UndefinedAdapter, self).__init__(message, *args, **kwargs)


class FrozenObject(AttributeError):
    """Cannot set attributes in frozen objects."""


class ReadonlyAttribute(AttributeError):
    """Should be thrown when some tries to access a readonly attribute."""


class UnsupportedResolution(ValueError):
    """Grid should respect vendor grid specification."""


class OverlappedChannels(ValueError):
    """Grid channels must be disjoint."""


class OutOfRange(ValueError):
    """Value should respect range specification by vendor."""
