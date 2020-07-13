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

ERRORMSG = {
    "error": {
        "reason": "",
        "message": "",
        "code": 0,
        "time": "",
    }
}

COMMANDOK = {
    "status": {
        "code": 0,
        "name": "",
        "time": "",
    }
}

ROOTPAGE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<head>
    <title>WSS Agent Powered by HPN - University of Bristol</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <style type="text/css">
        body {
            background-color: #fff;
            color: #000;
            font-size: 0.9em;
            font-family: sans-serif,helvetica;
            margin: 0;
            padding: 0;
        }
        :link {
            color: #0000FF;
        }
        :visited {
            color: #0000FF;
        }
        a:hover {
            color: #3399FF;
        }
        h1 {
            text-align: center;
            margin: 0;
            padding: 0.6em 2em 0.4em;
            background-color: #c9002f;
            color: #ffffff;
            font-weight: normal;
            font-size: 1.75em;
            border-bottom: 2px solid #000;
        }
        h1 strong {
            font-weight: bold;
        }
        h2 {
            font-size: 1.1em;
            font-weight: bold;
        }
        .content {
            padding: 1em 5em;
        }
        .content-columns {
            /* Setting relative positioning allows for
            absolute positioning for sub-classes */
            position: relative;
            padding-top: 1em;
        }
        .content-column-left {
            /* Value for IE/Win; will be overwritten for other browsers */
            width: 47%;
            padding-right: 3%;
            float: left;
            padding-bottom: 2em;
        }
        .content-column-right {
            /* Values for IE/Win; will be overwritten for other browsers */
            width: 47%;
            padding-left: 3%;
            float: left;
            padding-bottom: 2em;
        }
        .content-columns>.content-column-left, .content-columns>.content-column-right {
            /* Non-IE/Win */
        }
        img {
            border: 2px solid #fff;
            padding: 2px;
            margin: 2px;
        }
        a:hover img {
            border: 2px solid #3399FF;
        }
    </style>
</head>

<body>
  <div class="divTable" style="border: 2px solid #000;">
	<div class="divTableBody">
		<div class="divTableRow">
			<div class="divTableCell">
        <img src="https://people.maths.bris.ac.uk/~macpd/logo_transparent.gif" width="260" height="80">
      </div>
      <div class="divTableCell">
        <h1>WSS Agent - REST API Interface<br>
            High Performance Networks Group</strong>
        </h1>
      </div>
		</div>
		<div class="divTableRow">
			<div class="divTableCell">&nbsp;</div>
		</div>
	</div>
</div>
</body>
</html>
"""
