from time import sleep
from evdev import ecodes as e
from enum import Enum

from device import Tv,Receiver, HTPC
from config import *


class Event(object):
    def __init__(self):
        self.actions = {
            "volumeup": Receiver.volumeup,
            "volumedown": Receiver.volumedown}
        self.start_delay = 8

    def keyaction(self,keyname):
        if keyname in self.actions:
            self.actions[keyname]()

    def activate(self,poweron):
        Tv.poweron()
        if poweron:
            Receiver.poweron()
            sleep(self.start_delay)

    def deactivate(self,poweroff=False):
        if poweroff:
            Tv.poweroff()
            Receiver.poweroff()
            HTPC.sleep()


class HTPCEvent(Event):
    def  __init__(self):
        super().__init__()
        self.pulse_names = [self.NAME]
        self.pulse_id = ""
        self.receiver_mode = None

    def activate(self, poweron=False):
        HTPC.wake()
        super().activate(poweron)
        Tv.input("hdmi3")
        Receiver.input("htpc")
        Receiver.mode(self.receiver_mode)
        HTPC.unmute_app(self.pulse_names)
        HTPC.cont_service(self.pulse_names[0])
        HTPC.input(self.NAME)

    def deactivate(self,poweroff=False):
        if isinstance(self,PauseEvent):
           self.pause()
        HTPC.stop_service(self.pulse_names[0])
        HTPC.mute_app(self.pulse_names)
        super().deactivate(poweroff)


class MouseEvent(object):
    def mouseaction(self,events):
        if HTPC.awake:
            HTPC.mouseaction(events)


class PauseEvent(object):
    def pause(self):
        HTPC.pause(self.NAME)


class WatchTv(Event):
    NAME = WATCHTV
    def __init__(self):
        super().__init__()
        self.start_delay = 8
        self.actions = dict(self.actions, **{
            "up": Tv.channelup,
            "down": Tv.channeldown,
            "play": Receiver.mute})

    def activate(self, poweron=False):
        super().activate(poweron)
        HTPC.sleep()
        Tv.input("tv")
        Receiver.input("tv")
        Receiver.mode("dolby")


class Kodi(HTPCEvent, PauseEvent):
    NAME = KODI
    def __init__(self):
        super().__init__()
        self.receiver_mode = "dolby"
        self.actions = dict(self.actions, **{
            "play": lambda: HTPC.keycombo([e.KEY_PLAY]),
            "back": lambda: HTPC.keycombo([e.KEY_BACKSPACE]),
            "home": lambda: HTPC.keycombo([e.KEY_ESC]),
            "up": lambda: HTPC.keycombo([e.KEY_UP]),
            "down": lambda: HTPC.keycombo([e.KEY_DOWN]),
            "left": lambda: HTPC.keycombo([e.KEY_LEFT]),
            "right": lambda: HTPC.keycombo([e.KEY_RIGHT]),
            "menu": lambda: HTPC.keycombo([e.KEY_C]),
            "ok": lambda: HTPC.keycombo([e.KEY_ENTER])})


class Spotify(HTPCEvent, MouseEvent, PauseEvent):
    NAME = SPOTIFY
    def __init__(self):
        super().__init__()
        self.receiver_mode = "direct"
        self.actions = dict(self.actions, **{
            "left": lambda: HTPC.keycombo([e.KEY_LEFTCTRL,e.KEY_LEFT]),
            "right": lambda: HTPC.keycombo([e.KEY_LEFTCTRL, e.KEY_RIGHT]),
            "up": lambda: HTPC.keycombo([e.KEY_UP]),
            "down": lambda: HTPC.keycombo([e.KEY_DOWN]),
            "ok": lambda: HTPC.keycombo([e.KEY_SPACE]),
            "play": lambda: HTPC.keycombo([e.KEY_SPACE])})


class WatchPlay(HTPCEvent, MouseEvent):
    NAME = WATCHPLAY
    def __init__(self):
        super().__init__()
        self.receiver_mode = "dolby"
        self.pulse_names = ["firefox","plugin-container"]
        self.actions = dict(self.actions, **{
            "home": lambda: HTPC.keycombo([e.KEY_LEFTALT,e.KEY_HOME]),
            "back": lambda: HTPC.keycombo([e.KEY_LEFTALT,e.KEY_LEFT]),
            "left": lambda: HTPC.keycombo([e.KEY_LEFTALT,e.KEY_LEFT]),
            "right": lambda: HTPC.keycombo([e.KEY_LEFTALT, e.KEY_RIGHT]),
            "up": lambda: HTPC.keycombo([e.KEY_UP]),
            "down": lambda: HTPC.keycombo([e.KEY_DOWN]),
            "ok": lambda: HTPC.keycombo([e.KEY_ENTER]),
            "play": lambda: HTPC.keycombo([e.KEY_SPACE])})

