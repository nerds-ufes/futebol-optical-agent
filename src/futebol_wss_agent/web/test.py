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
import json
import requests

url = 'http://127.0.0.1:8080/add/user'

data = {
    "token": "JCS39VlJ3ELIez2KBC3PzIY2duYqlXDdtzqEZB3dL0BNDCrlMMzS29YsYUdnrOWu",
    "CreateUserSSH": {
        "username": "xyz",
        "ssh-key": "AAAAB3NzaC1y6zvpeP1xKmPAJtE32F+kIvFs6nFmhcqgzbAkSnZ8S54mL+BsI1OB98AwF6RFn9CmYN1QIgw9OOsxalZyQGfFr== teste@teste-laptop"
    }
}

resp = requests.post(url=url, json=data)
data = json.loads(resp.text)

print data