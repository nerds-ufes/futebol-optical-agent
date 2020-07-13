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
import logging
import os.path
import sys

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.contrib.fixers import ProxyFix

from futebol_wss_agent.config.conn import Connector
from futebol_wss_agent.config.response import ROOTPAGE
from futebol_wss_agent.lib.finisar_serial_adapter import Adapter
from futebol_wss_agent.lib.grid import FixedGrid
from futebol_wss_agent.lib.utils import (frequency_to_wavelength,
                                         wavelength_to_frequency)
from futebol_wss_agent.lib.wss import Wss

logger = logging.getLogger()

app = Flask(__name__)
app.config.from_object(__name__)
conn = Connector()

def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        logger.error("Impossible to read file", exc_info=True)
        return str(exc)

@app.route('/')
def root_page():
    return render_template('index.html')

@app.route('/static_files/<path:path>')
def get_static(path):  # pragma: no cover
    complete_path = os.path.join(root_dir(), path)
    content = get_file(complete_path)
    return Response(content, mimetype="image/png")

@app.route('/wavelenght/', methods=['POST'])
def wavelenght():
    try:
        num = float(request.form.get('number', 0))
    except ValueError as ex:
        logger.error("Impossible to convert wavelength", exc_info=True)
        return jsonify({'frequency': 0.0})
    result = wavelength_to_frequency(num)
    data = {'frequency': result}
    data = jsonify(data)
    return data

@app.route('/frequency/', methods=['POST'])
def frequency():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    try:
        num = float(request.form.get('number', 0))
    except ValueError as ex:
        logger.error("Impossible to convert frequency", exc_info=True)
        return jsonify({'wavelenght': 0.0})
    num = float(request.form.get('number', 0))
    result = frequency_to_wavelength(num)
    data = {'wavelenght': result}
    data = jsonify(data)
    return data

@app.route('/api/v1/info', methods=['GET'])
def get_information():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return jsonify({'tasks': 1222})
    else:
        pass
    return jsonify({'tasks': 1222})

@app.route('/api/v1/create/grid', methods=['POST',])
def create_grid():
    if request.method == 'POST':
        content = request.json
        bandwidth = 50.0
        spacing = 0.0
        resolution = 12.5
        # 8.0
        # 6.25
        frequency_window = (191.325, 196.150)
        # (191.1, 196.5)
        # (191.325, 196.150)
        bandwidth = float(content.setdefault('bandwidth', 50.0))
        spacing = float(content.setdefault('spacing', 0))

        adapter = Adapter(
            resolution=resolution,
            frequency_window=frequency_window)
        f0 = 191.35 #FixedGrid.DEFAULT_FIRST_FREQUENCY - 6.25e-3
        grid = FixedGrid(
            bandwidth=bandwidth,
            spacing=spacing,
            first_frequency=f0)
        wss = Wss(grid, adapter)

        channels = (dict(channel) for channel in grid)
        result = [
            channel.update(index=i) or channel
            for i, channel in enumerate(channels)
        ]
        conn._grid = grid
        conn._adapter = adapter
        conn._wss = wss
        try:
            wss.commit()
        except Exception as ex:
            logger.error("Impossible to send commands to WSS", exc_info=True)
            result = {
                "error": str(ex),
            }
        if content:
            return jsonify(result)
    else:
        pass

@app.route('/api/v1/channel/set', methods=['POST',])
def set_configuration():
    if request.method == 'POST':
        content = request.json

        if content.get('channels', 0) != 0:
            for channel in content['channels']:
                cr = float(channel['frequency'][1])
                cl = float(channel['frequency'][0])
                conf = conn._grid[
                    'frequency', cl if cl != 0 else '':cr if cr != 0 else ''
                ]
                conf.port = channel['port']
                conf.attenuation = channel['attenuation']
           
            grid = conn._grid
            
            channels = (dict(channel) for channel in grid)
            result = [
                 channel.update(index=i) or channel
                 for i, channel in enumerate(channels)
            ]
            try:
                conn._wss.commit()
            except Exception as ex:
                logger.error("Impossible to send commands to WSS", exc_info=True)
                result = {
                    "error": str(ex),
                }
        if content:
            return jsonify(result)
    else:
        pass

@app.route('/api/v1/update', methods=['PATCH', 'PUT'])
def update_configuration():
    if request.method == 'PATCH' or request.method == 'PUT':
        content = request.json
        if content:
            return jsonify({"Not Implemented yet"})
    elif request.method == 'GET':
        return jsonify({"Not Implemented yet"})
    else:
        pass
    return jsonify({"OK"})

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    """
        adapter = Adapter()
        f0 = FixedGrid.DEFAULT_FIRST_FREQUENCY - 6.25e-3
        grid = FixedGrid(bandwidth=50.0, spacing=0.0, first_frequency=f0)
        wss = Wss(grid, adapter)

        grid_left = wss.grid['frequency', :194.65]
        grid_left.port = 1
        grid_left.attenuation = 0

        grid_right = wss.grid['frequency', 194.65:]
        grid_right.port = 3
        grid_right.attenuation = 5
        print("Configuration FixedGrid")
        wss.commit()
    """
    try:
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False)
    except:
        logging.critical('server: CRASHED: Got exception on main handler')
        logging.critical(traceback.format_exc())
        raise
