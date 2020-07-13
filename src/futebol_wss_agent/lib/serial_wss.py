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
import asyncio
import sys

import serial


class SerialWSS(object):
    def __init__(self, serial, ioloop=None):
        self._serial = serial
        # Asynchronous I/O requires non-blocking devices
        self._serial.timeout = 0
        self._serial.write_timeout = 0

        if ioloop is not None:
            self.loop = ioloop
        else:
            self.loop = asyncio.get_event_loop()
        self.loop.add_reader(self._serial.fd, self._on_read)
        self._rbuf = b''
        self._rbytes = 0
        self._wbuf = b''
        self._rfuture = None
        self._delimiter = None

    def _on_read(self):
        data = self._serial.read(4096)
        self._rbuf += data
        self._rbytes = len(self._rbuf)
        self._check_pending_read()

    def _on_write(self):
        written = self._serial.write(self._wbuf)
        self._wbuf = self._wbuf[written:]
        if not self._wbuf:
            self.loop.remove_writer(self._serial.fd)

    def _check_pending_read(self):
        future = self._rfuture
        if future is not None:
            # get data from buffer
            pos = self._rbuf.find(self._delimiter)
            if pos > -1:
                ret = self._rbuf[:(pos+len(self._delimiter))]
                self._rbuf = self._rbuf[(pos+len(self._delimiter)):]
                self._delimiter = self._rfuture = None
                future.set_result(ret)
                return future

    async def read_until(self, delimiter=b'\n'):
        while self._delimiter:
            await self._rfuture

        self._delimiter = delimiter
        self._rfuture = asyncio.Future()
        #future = self._check_pending_read()
        return await self._rfuture

    async def readline(self):
        return await self.read_until()

    async def write(self, data):
        need_add_writer = not self._wbuf

        self._wbuf = self._wbuf + data
        if need_add_writer:
            self.loop.add_writer(self._serial.fd, self._on_write)
        return len(data)

async def go_serial():
    ser = serial.Serial('/dev/ttys015', 9600) #, rtscts=True, dsrdtr=True)
    print(ser)
    aser = SerialWSS(ser)

    written = await aser.write(b'test 1\n')
    print('written', written)
    data = await aser.readline()
    print('got from readline', data)

    while True:
        await aser.write(b'.\n')
        data = await aser.readline()
        print('GOT!', data)
        await asyncio.sleep(2.78)

async def main():
    for n in range(120):
        await asyncio.sleep(1)
        print('n=%d' % n)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(go_serial())
    loop.run_until_complete(main())
