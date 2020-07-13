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
import re
import sys
import time

import serial

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class UndefinedAdapter(RuntimeWarning):
    """Avoid committing grid if adapter not specified."""

    DEFAULT_MESSAGE = "Please use a valid adapter when defining the grid."

    def __init__(self, message=DEFAULT_MESSAGE, *args, **kwargs):
        super(UndefinedAdapter, self).__init__(message, *args, **kwargs)


class MalformedResponse(ValueError):
    """Grid should respect vendor grid specification."""


class Serial(object):
    """[summary]
    Arguments:
        object {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    
    DEFAULT_CONFIGURATION = {
        'prompt_string': '\^?OK(\$FF66)?',
        'error_regex': re.compile(
            r'\^?(CER|AER|RER|VER)(\$[A-F0-9]{4})?\s*$', re.I),
        'eol': '\r\n'
    }

    def __init__(self, device='/dev/ttyUSB0', speed=115200):
        self._device = device
        self._speed = speed
        self._wss = serial.Serial(self._device, self._speed) #, rtscts=True, dsrdtr=True)
        self._buf = []
        self.config = Serial.DEFAULT_CONFIGURATION

    def command(self, cmd=None):
        print(cmd)
        if cmd:
            buf = StringIO()
            res = ""
            c = cmd + self.config['eol']
            self._wss.write(c.encode('utf-8'))
               
            time.sleep(1)

            while True:
                while self._wss.in_waiting:
                    r = self._wss.read()
                    buf.write(r.decode())
                    time.sleep(0)

                res = buf.getvalue()
                print(res)
                #if bool(re.match(self.config['prompt_string'], res.decode())):
                #    break
                if not self._wss.in_waiting:
                    break
            self._wss.flush()
            return res.strip()

    def flush(self):
        self._wss.flush()

    def send_line(self, cmd='', flush=True):
        self._wss.write(cmd.encode('utf-8'))
        if flush:
            self._wss.flush()

if __name__ == "__main__":
    test = Serial()
    print(test.command('^CHW 0$FECE\r\n'))
