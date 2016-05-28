import Pyro4
from xbmcjson import XBMC
import _thread as thread
from subprocess import run, PIPE
from evdev import UInput, InputEvent, ecodes as e
from time import sleep

from pulse_mute import Pulse

class RemoteServer(object):
    def __init__(self):
        self.ui = UInput()
        cap = {e.EV_REL: [e.REL_X, e.REL_Y]}
        cap = {
            e.EV_REL : (e.REL_X, e.REL_Y),
            e.EV_KEY : (e.BTN_MOUSE,),
        }
        self.mouse = UInput(cap)

    def handshake(self):
        return "Server is up"

    @Pyro4.oneway
    def sleep(self):
        proc = run(["sudo","pm-suspend"], check=False)

    def keycombo(self,keys):
        for key in keys:
            self.ui.write(e.EV_KEY, key, 1)
        for key in keys:
            self.ui.write(e.EV_KEY, key, 0)
        self.ui.syn()

    def mouseaction(self, events):
        for ev in events:
            self.mouse.write(ev['type'],ev['code'],ev['value'])
        self.mouse.syn()

    def pause(self,appname):
        if appname == "spotify":
            self.pause_spotify()
        elif appname == "kodi":
            self.pause_kodi()

    def pause_spotify(self):
        args = ["dbus-send", "--print-reply",
                "--dest=org.mpris.MediaPlayer2.spotify",
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player.Pause"]
        proc = run(args, check=False)
        proc.check_returncode()

    def pause_kodi(self):
        kodi = XBMC("http://192.168.1.75:8080/jsonrpc")
        playerid_result = kodi.Player.GetActivePlayers()['result']
        if playerid_result:
            playerid = playerid_result[0]['playerid']
        else:
            return
        speed = kodi.Player.GetProperties(
            {'playerid':playerid,'properties':['speed']}
                )['result']['speed']
        if speed != 0:
            kodi.Player.PlayPause({'playerid': playerid})

    def mute_app(self, appname):
        Pulse.mute_input(appname)

    def unmute_app(self, appname):
        Pulse.unmute_input(appname)

    @Pyro4.oneway
    def pause_service(self,appname):
        proc = run(["systemctl","--user","kill","-s","STOP","%s.service" %appname],
                   check=False,stdout=PIPE)
        print(proc.stdout)
        sleep(2)

    def continue_service(self,appname):
        proc = run(["systemctl","--user","kill","-s","CONT","%s.service" %appname],
                   check=False,stdout=PIPE)
        print(proc.stdout)

def start_nameserver():
    Pyro4.naming.startNSloop(host,port)

host = "192.168.1.75"
port = 9093
thread.start_new_thread(start_nameserver,())
rs = RemoteServer()
daemon = Pyro4.Daemon(host)
rs_uri = daemon.register(rs)
ns = Pyro4.locateNS(host,port)
ns.register("zteifel.remoteserver", rs_uri)
print(ns.list())
daemon.requestLoop()
