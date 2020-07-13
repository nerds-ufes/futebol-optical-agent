#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017-2022 Rafael S. Guimaraes, Univertity of Bristol
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

import json
import sys
from contextlib import contextmanager
from warnings import warn

from jsondiff import diff

from .grid import Grid
from .verification import UndefinedAdapter


class Wss(object):
    """Data structure that represents a WSS"""

    def __init__(self, channels, adapter=None):
        self.previous_state = None
        self.grid = channels
        self.adapter = adapter
        if self.adapter is None:
            warn("No adapter specified for WSS.", UndefinedAdapter)
        self._run_adapter_hook('init')

    def _run_adapter_hook(self, name, *args, **kwargs):
        """\
        If adapter provide hook, run it, with the object as first argument.
        """
        if hasattr(self.adapter, name):
            return getattr(self.adapter, name)(self, *args, **kwargs)
        return None

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, value):
        self._grid = Grid(sorted(value, key=lambda ch: ch.central_frequency))

    def commit(self):
        """Use the given adapter to send the pending changes to the equipment.

        After committing the previous state is updated to the current state.
        """
        try:
            self._run_adapter_hook('validate')
            self._run_adapter_hook('commit')
        except Exception as err:
            raise
        else:
            self.previous_state = self.grid.copy().freeze()

    @contextmanager
    def transaction(self):
        """Creates a context were several properties can be updates, and after
        if commit the change.
        """
        self._run_adapter_hook('begin_transaction')
        try:
            yield
            self.commit()
        except Exception as err:
            if self._run_adapter_hook('rescue_transaction', err) is False:
                raise err
        else:
            self._run_adapter_hook('finish_transaction')

    def changes(self, **kwargs):
        """Dictionary difference between current and previous state."""
        options = dict(syntax='explicit')
        options.update(kwargs)
        options.update(dump=True)
        # Dumping jsondiff and loading it again ensures a plain dict delta
        return json.loads(
            diff([dict(ch) for ch in (self.previous_state or [])],
                 [dict(ch) for ch in self.grid], **options)
        )
    diff = changes

    @property
    def dirty(self):
        """True if any channel changed since the last commit."""
        return bool(self.changes(syntax='symmetric'))
