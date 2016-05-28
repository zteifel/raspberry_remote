from remote import Mini_remote as Mini
from events import WatchTv, WatchPlay, Spotify, Kodi
from events import MouseEvent, PauseEvent
from time import time

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

    def switch_event(self, Event, poweron):
        if not isinstance(self.active_event, Event):
            if self.active_event:
                self.active_event.deactivate()
                self.inactive_events[self.active_event.NAME] = self.active_event
            self.active_event = self.inactive_events.pop(Event.NAME)
            if poweron:
                self.active_event.activate(poweron)
            else:
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
                            print("active hotkey: %s" % self.active_modkey)

                    elif self.active_modkey == "ok":
                        self.active_modkey = None
                        if self.active_event:
                            poweron = False
                        else:
                            poweron = True
                        if keyname in self.input_keys:
                            self.switch_event(self.input_keys[keyname],poweron)

                    elif self.active_event:
                        self.active_modkey = None
                        self.active_event.keyaction(keyname)

                    else:
                        self.active_modkey = None

print("Initializing...",end="")
m = Main()
print("Done!")
m.eventhandler()


