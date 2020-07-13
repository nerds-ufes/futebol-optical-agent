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

GUNICORN=$(which gunicorn 2> /dev/null)
APP_PATH="/usr/local/proxyssh/"
PIDFILE="/var/run/proxyssh.pid"

start() {
    echo "Starting WSS Agent - REST API..."
    if [ -x $GUNICORN ]
    then
        cd $APP_PATH
        $GUNICORN -D -p $PIDFILE -b 0.0.0.0:8080 app_web:app
        echo "Application now is running..."
    else
        echo "Application cannot start: Gunicorn not found!"
    fi
}

stop() {
    if [ -f $PIDFILE ]
    then
        kill $(cat $PIDFILE)
    else
        echo "PIDFILE not found!"
    fi
}

restart(){
    stop
    start
}

status(){
    echo
}

case "$1" in
    start)
        start
        RETVAL=$?
        ;;
    stop)
        stop
        RETVAL=$?
        ;;
    restart)
        restart
        RETVAL=$?
        ;;
    status)
        RETVAL=$?
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        RETVAL=2
esac
