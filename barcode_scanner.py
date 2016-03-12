#!/usr/bin/python

DEBUG = False

import sys
from select import select
from evdev import InputDevice, ecodes, list_devices

scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

#devices = [InputDevice(fn) for fn in glob.glob('/dev/input/by-id/usb-Sycreader*')]
#
devices = map(InputDevice, list_devices())


fdevices = filter(lambda x: 'Sycreader RFID Technology' in x.name, devices)
devices = {dev.fd: dev for dev in fdevices}

for k, dev in devices.items():
    dev.grab()
    sys.stderr.write("{} {} {}\n".format(dev.fn, dev.name, dev.phys))

buf = {dev.fd: [] for dev in fdevices}


def handle(i, event):
    if event.type == ecodes.EV_KEY and event.value:

        sc = scancodes[event.code]
        if DEBUG:
            sys.stderr.write("Dev {}, {}\n".format(i.fd, sc))
        if sc == 'CRLF':
            print("".join(buf[i.fd]))
            sys.stderr.write("Msg from:{} '{}'\n".format(i.fd, "".join(buf[i.fd])))
            sys.stdout.flush()
            buf[i.fd] = []
        else:
            buf[i.fd].append(sc)


while True:
    r, w, x = select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            handle(devices[fd], event)
