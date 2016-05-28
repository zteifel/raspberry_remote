import Pyro4
from xbmcjson import XBMC
import _thread as thread
from subprocess import run, PIPE
from evdev import UInput, InputEvent, ecodes as e
from time import sleep
import logging as log

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

    def run(self, args):
        proc = run(args, check=False, stdout=PIPE, stderr=PIPE)
        return (args, proc.returncode, proc.stderr,proc.stdout)

    def handshake(self):
        return

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
            return self.pause_spotify()
        elif appname == "kodi":
            return self.pause_kodi()

    def pause_spotify(self):
        args = ["dbus-send", "--print-reply",
                "--dest=org.mpris.MediaPlayer2.spotify",
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player.Pause"]
        return self.run(args)

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

    def pause_service(self,appname):
        args = ["systemctl","--user","kill","-s","STOP","%s.service" %appname]
        result = self.run(args)
        sleep(2)
        return result

    def continue_service(self,appname):
        args = ["systemctl","--user","kill","-s","CONT","%s.service" %appname]
        return self.run(args)

def init_log():
    log_format = '%(levelname)s:%(message)s'
    log_file = '/home/zteifel/remote/server.log'
    log.basicConfig(format=log_format, level=log.DEBUG,filename=log_file)

def start_nameserver():
    Pyro4.naming.startNSloop(host,port)

init_log()
log.info('Starting remote server')
host = "192.168.1.75"
port = 9093
thread.start_new_thread(start_nameserver,())
rs = RemoteServer()
daemon = Pyro4.Daemon(host)
rs_uri = daemon.register(rs)
ns = Pyro4.locateNS(host,port)
ns.register("zteifel.remoteserver", rs_uri)
daemon.requestLoop()
