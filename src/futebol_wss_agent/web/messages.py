#!/usr/bin/python
# coding: utf-8
# ---------------------------------------------------------------------------------
# O2CMF
# Copyright (C) 2016-2019  Rafael Silva Guimarães
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ---------------------------------------------------------------------------------
import grp
import os
import pwd
from datetime import datetime

import sh

import config
import response as resp


class Message(object):

    def __init__(self):
        pass

    def execute(self):
        """
        Perform instructions
        """
        raise NotImplementedError

class FactoryMessage(object):
    @classmethod
    def handle(cls, msg=""):
        try:
            if "token" in msg:
                if msg["token"] == config.TOKEN:
                    if "Read" in msg:
                        return AddUserSSHMessage(msg)
                    elif "AddSshKey" in msg:
                        return AddSshKeyMessage(msg)
                    elif "ListUsersSSH" in msg:
                        raise NotImplementedError
                    elif "DeleteUserSSH" in msg:
                        return DeleteUserSSHMessage(msg)
                    else:
                        return ErrorMessage(
                            {"reason": "options", "message": "Invalid Option", "code": 404}
                        )
                else:
                    return ErrorMessage(
                        {"reason": "token", "message": "Invalid Token", "code": 404}
                    )
            else:
                return ErrorMessage(
                    {"reason": "option", "message": "Token not found", "code": 404}
                )
        except Exception as ex:
            print("Error: JSON message cannot be read! {}".format(str(ex.message)))
