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

from serial_wss import SerialWSS


class HandleWSS(object):
    def __init__(self, **kwargs):
        self._device = '/dev/cu.UC-232AC'
        self._speed = 115200
        self._wss = serial.Serial(self._device, self._speed) #, rtscts=True, dsrdtr=True)
        self._wss = SerialWSS(self._wss)

    async def goserial(self, data=None, future=None):
        #print(self._wss)
        #print('written', written)
        data = await self._wss.readline()
        print('got from readline', data)
        while True:
            #await self._wss.write(b'.\n')
            data = await self._wss.readline()
            #print('GOT!', data)
            future.set_result(data)
            await asyncio.sleep(2.78)

    async def read_reconfiguration_array(self):
        """This query reads the configuration of all channels in the channel plan.
           RRA?\r{\n}
           <C>,<P>,<A>{;<C>,<P>,<A>}*(0:Cmax-1)\r\n
           OK\r\n
        """
        await test._wss.write("RRA?\r\n".encode())


    async def update_reconfiguration_array(self, **conf):
        """This command will instruct the device to prepare
           a new channel array (LCoS pattern) for all channels.
           <C> if in FlexgridTM mode is a channel number between [Cini:Cmax] previously
               defined by DCC command. If in Fixed 50GHz or 100GHz mode is a channel 
               number between [0:Cmax-1] as defined in the channel plan.
           <P> is the port number between [1:Pmax] to which channel <C> is assigned.
               If equal to 99 then <C> is blocked by port.
           <A> is the attenuation between [0.0:Amax] assigned to channel <C>.
               If equal to 99.9 then <C> is blocked by attenuation.
            ^URA 0,99,99.9;1,99,99.9;2,99,99.9;3,99,99.9;\r\n
            ^OK$FF66\r\n
        """
    async def define_custom_channel(self, **conf):
        """This command allocates spectral slices to corresponding channels in order 
           to create a FlexgridTM channel plan. This command automatically assigns
           a symmetrical range5 of the maximum allowable channel bandwidth for the 
           channel being defined. This range defines the spectral allocation the channel
           may grow into hitlessly. However, the range does not reserve this spectrum
           for this channel.
           <C> is a channel number between [Cini:Cmax].
           <S>:<S> is the interval of FlexgridTM slices
           assignedto <C>. <S> is between [1:Smax].
           Ex. 
                DCC 1=1:8;10=9:12;3=14:17;9=350:373;\r{\n}
                OK\r\n
        """
        pass
    
    async def query_custom_channels(self):
        """This query returns the current channel plan as a semi-colon delimited list.
            DCC?\r{\n}
            <C>=<S>:<S>{;<C>=<S>:<S>}*(0:Cmax-1)\r\n
            OK\r\n
        """
        await test._wss.write("DCC?\r\n".encode())
    
    async def start_up_state(self):
        """This query reads the current start-up state of the device
           (SLS = Start Last Saved, SAB = Start All Blocked, SFD = Start Factory Default).
           SUS?\r{\n}
           [SLS|SAB|SFD]\r\n
           OK\r\n
        """
        await test._wss.write("SUS?\r\n".encode())
    
    async def firmware_release(self):
        """This query will return the firmware release version number active on the device.
           FWR?\r{\n}
           [01:255].[00:255].[00:255]{_rc}{[00:255]}\r\n
           OK\r\n
        """
        await test._wss.write("FWR?\r\n".encode())

    async def hardware_release(self):
        """This query will return the hardware release for the device (FPGA version).
           HWR?\r{\n}
           [00:255].[00:255].[00:255]\r\n
           OK\r\n
        """
        await test._wss.write("HWR?\r\n".encode())

    async def serial_number(self):
        """This query will return the device serial number.
           SNO?\r{\n}
           [EP|EF|SN][000000:999999]\r\n
           OK\r\n
        """
        await test._wss.write("SNO?\r\n".encode())
    
    async def operation_status(self):
        """This query returns the operational status of the device.
           OSS?\r{\n}
           [0x0000:0xFFFF]\r\n
           OK\r\n
        """
        await test._wss.write("OSS?\r\n".encode())


async def main(t):
    for n in range(120):
        await asyncio.sleep(1)
        print('n=%d' % n)
        if ( n == 5):
            res = "teste {}\n".format(n)
            await test.query_custom_channels()
            
def got_result(future):
    print(future.result())

if __name__ == "__main__":
    test = HandleWSS()
    loop = asyncio.get_event_loop()
    future1 = asyncio.Future()
    future1.add_done_callback(got_result)
    asyncio.ensure_future(test.goserial(future=future1))
    a, b = loop.run_until_complete(main(test))
    print(a)
    print(b)
