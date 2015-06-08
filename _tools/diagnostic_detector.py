#!/usr/bin/env python
# coding=utf-8
# Stan January 25, 2010

import pygtk
pygtk.require("2.0")
import gtk, gobject, serial
#~ import gtkfilling

current_port   = 1          # График какого аналог. выхода выводить?
timeout_read   = 200        # Интервал чтения из порта (мсек)
timeout_redraw = 500        # Интервал обновления графика (мсек)


try:
    usbport = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
except Exception, e:
    import sys
    sys.exit(e)

# Переменные для хранения значений
value_history = []                  # Массив возращаемых из порта значений
value_cash = ''                     # Первое значение сначала кешируем
offset_history = 0                  # Длина value_history

# Переменные для отображения
cursor = 0                          # Значение offset_history на нуле
auto_rewind = 0                     # Пока не реализовано
value_list = []                     # Массив текущих значений

def ReadAll():
    global value_history, value_cash, offset_history, cursor, value_list
    text = usbport.read(1)          # read one, with timout
    if text:                        # check if not timeout
        n = usbport.inWaiting()     # look if there is more to read
        if n:
            text = text + usbport.read(n)   #get it

        text = text.replace("\r", "")
        allvalues_list = text.split("\n")
# Пример allvalues_list: ['1;316;318;313;313', '2;295;316;295;313', '']
# Если строка успела вернуться полностью, то последняя ячейка будет пустая
# Первая ячейка может быть не полной
        allvalues_list[0] = value_cash + allvalues_list[0]
        for v in allvalues_list[0:-1]:
            try:
                value_list = v.split(";")
            except Exception, e:
                value_list = []
                print e

            if value_list:
                value_history.append(value_list)
                offset_history += 1

            if offset_history - cursor > 800:
                cursor = offset_history

        value_cash = allvalues_list[-1]
    return True

def Redraw():
    lab.area.window.show()
    return True


class Labels:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", lambda w: gtk.main_quit())

        self.window.set_title("Detector Diagnostic")
        self.window.set_size_request(1000, 500)
        self.window.set_border_width(5)
        hbox = gtk.HBox(False, 5)
        self.window.add(hbox)

        vbox = gtk.VBox(False, 5)
        vbox.set_size_request(140,200)
        hbox.pack_start(vbox, False, False, 0)

        frame = gtk.Frame("Analog")
        self.analog_label = gtk.Label("")
        self.analog_label.set_justify(gtk.JUSTIFY_LEFT)
        frame.add(self.analog_label)
        vbox.pack_start(frame, False, False, 0)

        frame = gtk.Frame("Digital")
        self.digital_label = gtk.Label("")
        self.digital_label.set_justify(gtk.JUSTIFY_LEFT)
        frame.add(self.digital_label)
        vbox.pack_start(frame, False, False, 0)

        frame = gtk.Frame("x")
        self.x_label = gtk.Label("")
        self.x_label.set_justify(gtk.JUSTIFY_LEFT)
        frame.add(self.x_label)
        vbox.pack_start(frame, False, False, 0)

        frame = gtk.Frame("Options")
        label = gtk.Label("current_port: %s\ntimeout_read: %s\ntimeout_redraw: %s" %
                (current_port, timeout_read, timeout_redraw))
        label.set_justify(gtk.JUSTIFY_LEFT)
        frame.add(label)
        vbox.pack_start(frame, False, False, 0)

        vbox = gtk.VBox(False, 5)
        hbox.pack_start(vbox)

        frame = gtk.Frame("Graph")
        self.area = gtk.DrawingArea()
        self.pangolayout = self.area.create_pango_layout("")

        self.sw = gtk.ScrolledWindow()
        self.sw.add_with_viewport(self.area)
        self.table = gtk.Table(2, 2)
        self.hruler = gtk.HRuler()
        self.vruler = gtk.VRuler()
        self.hruler.set_range(0, 100, 0, 100)
        self.vruler.set_range(0, 100, 0, 100)
        self.table.attach(self.hruler, 1, 2, 0, 1, yoptions=0)
        self.table.attach(self.vruler, 0, 1, 1, 2, xoptions=0)
        self.table.attach(self.sw, 1, 2, 1, 2)
        frame.add(self.table)
        self.area.connect("expose-event", self.area_expose_cb)
        vbox.pack_start(frame)

        self.window.show_all()

    def area_expose_cb(self, area, event):
        analog_str = ""
        for i in value_list:
            analog_str += "%s\n" % i
        self.analog_label.set_text(analog_str)
        self.x_label.set_text("%s/%s" % (cursor, offset_history))

        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        for i in xrange(cursor, offset_history):
            try:
                y = int(value_history[i][current_port]) / 3
            except:
                y = 0
            x = i - cursor
            self.area.window.draw_line(self.gc, x, 0, x, y)
        return True

lab = Labels()


def main():
    gobject.timeout_add(timeout_read, ReadAll)
    gobject.timeout_add(timeout_redraw, Redraw)
    gtk.main()
    return 0

if __name__ == "__main__":
    main()
