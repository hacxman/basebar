#!/usr/bin/python
# !!! NOTWorking, reconnection works but reading does not
import sys
import select
import functools

import pyudev
from evdev import InputDevice, ecodes, list_devices

DEV_IDENT = 'Sycreader RFID'

scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

devices = map(InputDevice, list_devices())
devices = filter(lambda x: DEV_IDENT in x.name, devices)
devices = {dev.fd: dev for dev in devices}

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='input')
monitor.start()

fds = {monitor.fileno(): monitor}
for fd, dev in devices.items():
    dev.grab()
    print(dev.fn, dev.name, dev.phys)
    #fds[fd] = dev


buf = {}


def handle(i, event):
    if event.type == ecodes.EV_KEY and event.value:
        #print("Dev {}, {}".format(i.fd, scancodes[event.code]))
        c = scancodes[event.code]

        if i.fd not in buf:
            buf[i.fd] = ''

        if c == 'CRLF':
            print(buf[i.fd])
            sys.stdout.flush()

            buf[i.fd] = ''
        else:
            buf[i.fd] += c


finalizers = []

while True:
    r, w, x = select.select(fds, [], [])

    if monitor.fileno() in r:
        r.remove(monitor.fileno())

        for udev in iter(functools.partial(monitor.poll, 0), None):
            # we're only interested in devices that have a device node
            # (e.g. /dev/input/eventX)
            if not udev.device_node:
                break

            # find the device we're interested in and add it to fds
            for name in (i['NAME'] for i in udev.ancestors if 'NAME' in i):
                if DEV_IDENT in name:
                    print('ACT', udev.action)
                    if udev.action == u'add':
                        print('Device added: %s' % udev.device_node)
                        dev = InputDevice(udev.device_node)
                        dev.grab()
                        #fds[monitor.fileno()] = dev
                        fds[monitor.fileno()] = dev

                    elif udev.action == u'remove':
                        print('Device removed: %s' % udev.device_node)

                        def helper():
                            global fds
                            fds = {monitor.fileno(): monitor}

                        finalizers.append(helper)
                        break

                        tfd = -1
                        for fd, dev in fds.items():
                            if dev.fn == udev.device_node:
                                print 'GOTCHA'
                                break


                        if tfd:
                            def helper():
                                global fds
                                #fds = {monitor.fileno(): monitor}
                                del fds[tfd]
                            finalizers.append(helper)
                        break

    for fd in r:
        dev = fds[fd]
        for event in dev.read():
            handle(dev, event)

    for i in range(len(finalizers)):
        finalizers.pop()()

    print fds
