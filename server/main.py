from remote import NewRemote as Remote
from events import WatchTv, WatchPlay, Spotify, Kodi
from events import MouseEvent, PauseEvent
from lamp import Lamp, LampGroup
import time
import logging as log


class Main(object):

    def __init__(self):
        self.active_event = None
        self.lamp_timeout = 10
        self.double_timeout = 0.3
        self.inactive_events = {
            Spotify.NAME: Spotify(),
            Kodi.NAME: Kodi(),
            WatchTv.NAME: WatchTv(),
            WatchPlay.NAME: WatchPlay()
        }
        self.input_keys = {
            "up": Kodi,
            "down": WatchTv,
            "left": Spotify,
            "right": WatchPlay
        }
        self.lamp_keys = {
            "up": "ceiling",
            "left": "bed",
            "right": "sofa",
            "down": "all"
        }
        self.lamp_group = LampGroup({
            "sofa": Lamp(100,1),
            "ceiling": Lamp(100,2),
            "bed": Lamp(100,3),
        })
        self.remotes = [Remote()]
        self.active_modkey = None

    def switch_event(self, event, poweron):
        if not isinstance(self.active_event, event):
            if self.active_event:
                self.active_event.deactivate()
                self.inactive_events[self.active_event.NAME] = self.active_event
            self.active_event = self.inactive_events.pop(event.NAME)
            if poweron:
                log.info("Powering on event: %s" % event.NAME)
                self.active_event.activate(poweron)
            else:
                log.info("Switching event to: %s" % event.NAME)
                self.active_event.activate()

    def read_key(self,remote,timeout=None):
       event = remote.event(timeout)
       if event:
            action, ev = event
            return ev['keyname']

    def lamp_mode(self,remote):
        last_activity = time.time()
        first_key = None
        first_time = None
        while time.time() - last_activity < self.lamp_timeout:
            keyname = self.read_key(remote,-1)
            # Single press
            if first_key and time.time() - first_time > self.double_timeout:
                if first_key == "down":
                    self.lamp_group.toggle()
                    log.debug("toggle all lights")
                else:
                    lamp = self.lamp_keys[first_key]
                    self.lamp_group.lamps[lamp].toggle()
                    log.debug("toggle light %s" % lamp)
                first_key = None
            # No press
            elif not keyname:
                continue
            # Exit lamp mode due to other than lamp key
            elif keyname not in self.lamp_keys:
                return
            # First press
            elif not first_key:
                first_key = keyname
                first_time = time.time()
            # Double press
            else:
                if keyname != first_key:
                    first_key = keyname
                    first_time = time.time()
                else:
                    first_key = None
                    lamp =  self.lamp_keys[keyname]
                    self.lamp_group.lamps[lamp].dim()
                    log.debug("dimming light %s" % lamp)
            last_activity = time.time()

        log.debug("Exiting lamp mode by timeout")


    def eventhandler(self):
        while True:
            for remote in self.remotes:
                event = remote.event()
                if event:
                    action, ev = event
                else:
                    continue

                if action and action == 'mouse':
                    if self.active_event and isinstance(self.active_event,MouseEvent):
                         self.active_event.mouseaction(ev)

                elif action and action == 'kbd':
                    keyname = ev['keyname']

                    if ev['pressmode'] == 'long':
                        log.debug('Key long press: %s' % keyname)
                        self.active_modkey = keyname

                    elif keyname == "power":
                        self.active_modkey = None
                        if self.active_event:
                            self.active_event.deactivate(poweroff=True)
                            event = self.active_event
                            name = event.NAME
                            self.inactive_events[name] = event
                            self.active_event = None

                    elif keyname == "home":
                        self.active_modkey = None
                        log.debug('Lamp mode activated: %s' % keyname)
                        self.lamp_mode(remote)

                    elif (self.active_modkey == "ok" or
                          self.active_modkey == "power"):
                        if keyname in self.input_keys:
                            if self.active_event:
                                poweron = False
                            else:
                                poweron = True
                            log.debug('Input key pressed: %s' % keyname)
                            self.switch_event(self.input_keys[keyname],poweron)
                        self.active_modkey = None

                    elif self.active_event:
                        self.active_modkey = None
                        log.debug('Key pressed: %s' % keyname)
                        self.active_event.keyaction(keyname)
                    else:
                        log.debug('Key not defined pressed: %s' % keyname)
                        self.active_modkey = None

def init_log():
    log_date= '%d-%m-%Y %H:%M:%S'
    log_format = '%(asctime)s %(levelname)s:%(message)s'
    log_file = '/home/alarm/remote/remote.log'
    log.basicConfig(format=log_format, level=log.DEBUG,
                    datefmt=log_date, filename=log_file)

init_log()
log.info("Starting initialization...")
m = Main()
log.debug("Initializing done!")
m.eventhandler()


