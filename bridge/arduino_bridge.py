#!/usr/bin/env python
# coding=utf-8
# Stan 2011-01-15

# Copyright (C) Stan 2011 <lishnih@gmail.com>
#
# <This package> is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# <This package> is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Скрипт взаимодействия с платой Arduino.
Предполагается, что плата Arduino используется в связке с самоходной установкой,
типа Crowler, а USB портом подключена к дополнительному бортовому компьютеру.
Требования к бортовому компьютеру:
  - Python 2.7;
  - Сеть WiFi.
На бортовом компьютере и запускается данный скрипт.
Скрипт, по сути, является сервером и позволяет подключаться клиентам из
сети WiFi. Скрипт устанавливает соединение с платой Arduino и становится
связующим мостом между клиентами и платой.

P.S. Желательно, чтобы на бортовом компьютере была установлена система Linux и
программа watchdog, которая будет следить, чтобы этот скрипт всегда был запущен.
"""

# import os, atexit, traceback
# localdir = os.path.dirname(__file__)
# @atexit.register
# def exitfunc():
#     tb = traceback.format_exc()
#     if tb != 'None\n':
#         f = open(os.path.join(localdir, "fatal.err"), "w")
#         f.write(tb)


import SocketServer
import os, time, traceback

import lib.enhancedserial as enhancedserial
import arduino_interpreter


def get_time_str(localtime = None):
    localtime = time.localtime(localtime)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
    tz = - time.timezone / 3600
    tz_pattern = "+%02d00" if tz >= 0 else "%03d00"
    tz_str = tz_pattern % tz
    return "%s %s" % (time_str, tz_str)

def print_ln(str):
    print str
    f.write("%s\n" % str)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            command = self.request.recv(1024).strip()
            response = arduino_interpreter.execute(s, command) if command else ""
            if not response:
                response = "<nothing>"
            if not s:
                response = "[Serial Arduino is closed!] %s" % response
            self.request.send(response)
            print_ln("%s: %s> %s" % (get_time_str(), self.client_address[0], command))
            print_ln("Response: %s" % response)
        except:
            tb = traceback.format_exc()
            print_ln(tb)


def server_func(options, args):
    global f, s

    # Открываем файл логов
    localdir = os.path.dirname(__file__)
    f = open(os.path.join(localdir, options.logfile), "a")

    # Записываем время запуска скрипта
    print_ln("%s: started!" % get_time_str())

    try:
        # Создаём сервер
        server = SocketServer.TCPServer((options.host, options.port), MyTCPHandler)

        # Открываем последовательный порт
        try:
            s = enhancedserial.EnhancedSerial(options.arduino)
        except enhancedserial.SerialException, e:
            s = None
            print_ln("Could not open port: %s!" % e)

        # Цикл
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print_ln("Keyboard Interrupt!")
    except:
        tb = traceback.format_exc()
        print_ln(tb)

    # Записываем время останова скрипта
    print_ln("%s: stopped!\n" % get_time_str())


if __name__ == "__main__":
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options]",
        description = "%prog - Bridge between Arduino and WiFi-clients."
    )

    parser.add_option("--host",
        dest = "host",
        default = "localhost",
        help = "host, default %default",
    )

    parser.add_option("--port",
        dest = "port",
        type = 'int',
        default = 2011,
        help = "port, a number (default %default)",
    )

    parser.add_option("-a", "--arduino",
        dest = "arduino",
        type = 'int',
        default = 8,
        help = "arduino com-port, a number (default %default)",
    )

    parser.add_option("--log",
        dest = "logfile",
        default = "bridge.log",
        help = "log file, default %default",
    )

    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non-error messages",
        default = False
    )

    (options, args) = parser.parse_args()

    server_func(options, args)
