#!/usr/bin/env python
# coding=utf-8
# Stan 2011-01-16

"""
Модуль обработки команд для кроулера.
"""

def execute(serial, command):
    if command[0] == '-':               # Простые команды (контролёра)
        command = command[1:]
        if serial:
            if   command == 'D1':       # Подать 1 на цифрофой выход 1
                pass
            elif command == 'd1':       # Подать 0 на цифрофой выход 1
                pass
            elif command == 'A1':       # Подать max на аналоговый выход 1
                pass
            elif command == 'a1':       # Подать 0 на аналоговый выход 1
                pass
            elif command == 'E1FA':     # Подать FA на аналоговый выход 1
                pass

            elif command == 'G1':       # Получить сигнал с цифрового входа 1
                pass
            elif command == 'R1':       # Получить сигнал с аналогового входа 1
                pass

            elif command == 'i':        # Данные о контролёре
                pass
            elif command == 'c':        # Данные об авторских правах
                pass
            elif command == 'v':        # Версия прошивки
                pass

            else:
                return "Unsupported simple command!"
        else:
            return ""

        serial.write(command)

    command = command.upper()

    # Сервисные команды (serial не требуется)
    if   command == 'VERSION':
        return "1.0"
    elif command == 'SCAN':
        from lib.scan import scan
        str = "Found ports:\n"
        for n, s in scan():
            str += "(%d) %s\n" % (n, s)
        return str

    else:                           # Команды кроулера
        if serial:
            if   command == 'CROWLER FORWARD':
                pass
            elif command == 'CROWLER BACK':
                pass

            else:
                return "Unsupported command!"
        else:
            return ""

    str = serial.readline()
    if str == "+\n":
        lines = serial.readlines()
        str = "\n".join(lines)
    return str
