from remote import Mini_remote as Mini
from events import WatchTv, WatchPlay, Spotify, Kodi
from events import MouseEvent, PauseEvent
from time import time
import logging as log

class Main(object):

    def __init__(self):
        self.active_event = None
        self.ide_time = 180 # min
        self.idle_start = time()
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
        self.remotes = [Mini()]
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
                        if keyname == "menu":
                            self.active_modkey = None
                            if self.active_event:
                                self.active_event.deactivate(poweroff=True)
                                event = self.active_event
                                name = event.NAME
                                self.inactive_events[name] = event
                                self.active_event = None
                        elif not self.active_modkey:
                            self.active_modkey = keyname

                    elif self.active_modkey == "ok":
                        self.active_modkey = None
                        if self.active_event:
                            poweron = False
                        else:
                            poweron = True
                        if keyname in self.input_keys:
                            log.debug('Input key pressed: %s' % keyname)
                            self.switch_event(self.input_keys[keyname],poweron)

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


