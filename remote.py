from evdev import InputDevice,categorize, ecodes, categorize
from selectors import DefaultSelector, EVENT_READ
from enum import IntEnum
import _thread as thread


class Mini_remote(object):

    def __init__(self):
        self.selector = DefaultSelector()
        self.init_hardware()
        self.mouseevents = []
        self.prev_value = 1
        self.keynames = {
            127: "menu",
            28: "ok",
            103: "up",
            108: "down",
            105: "left",
            106: "right",
            273: "back",
            172: "home",
            164: "play",
            114: "volumedown",
            115: "volumeup"}


    def init_hardware(self):
        path_dir = '/dev/input/by-path/'
        paths = (
            path_dir + 'platform-20980000.usb-usb-0:1.2:1.0-event-kbd',
            path_dir + 'platform-20980000.usb-usb-0:1.2:1.1-event-mouse',
            path_dir + 'platform-20980000.usb-usb-0:1.4:1.0-event-kbd',
            path_dir + 'platform-20980000.usb-usb-0:1.4:1.1-event-mouse')
        for path in paths:
            i = InputDevice(path)
            i.grab()
            self.selector.register(i,EVENT_READ)

    def event(self):
        for key, mask in self.selector.select():
            device = key.fileobj
            for ev in device.read():
                if ev.type == ecodes.EV_REL or ev.code == ecodes.BTN_MOUSE:
                    self.mouseevents.append(self.mouseaction(ev.type,ev.code,ev.value))
                elif ev.type == ecodes.SYN_REPORT:
                    tmp = self.mouseevents
                    self.mouseevents = []
                    return "mouse", tmp
                elif ev.type == ecodes.EV_KEY:
                    return self.keyaction(ev.code,ev.value)

    def mouseaction(self, _type, code, value):
        return {'type': _type, 'code': code, 'value': value}

    def keyaction(self, code, value):
        if value == 0 and self.prev_value == 0:
            return
        elif value == 0:
            keyname = self.keynames[code]
            if self.prev_value == 2:
                pressmode = 'long'
            else:
                pressmode = 'single'
            self.prev_value = value
            return "kbd", {'keyname': keyname, 'pressmode': pressmode}
        else:
            self.prev_value = value
