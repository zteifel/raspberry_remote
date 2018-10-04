from evdev import InputDevice,categorize, ecodes, categorize
from selectors import DefaultSelector, EVENT_READ
from enum import IntEnum
import _thread as thread

class NewRemote(object):

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
            1: "back",
            172: "home",
            114: "volumedown",
            115: "volumeup",
            116: "power",
            272: "btn_left"}


    def init_hardware(self):
        path_dir = '/dev/input/by-path/'
        paths = (
            path_dir + 'platform-20980000.usb-usb-0:1.2.1:1.0-event-kbd',
            path_dir + 'platform-20980000.usb-usb-0:1.2.1:1.1-event-mouse')

        for path in paths:
            i = InputDevice(path)
            i.grab()
            self.selector.register(i,EVENT_READ)

    def event(self,timeout=None):
        for key, mask in self.selector.select(timeout=timeout):
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

        if value == 1:
            self.prev_value = 1
            return

        if value == 2:
            if code == 28 or code == 272 or code == 116:
                self.prev_value = 2
                return
            else:
                self.prev_value = 1

        if self.prev_value == 2:
            pressmode = 'long'
        else:
            pressmode = 'single'

        keyname = self.keynames[code]
        self.prev_value = 0
        return "kbd", {'keyname': keyname, 'pressmode': pressmode}
