from subprocess import run, PIPE
from time import sleep
import sys
import traceback
import json
import Pyro4
from evdev import ecodes as e
from config import *

remoteserver = Pyro4.Proxy("PYRONAME:zteifel.remoteserver")
remoteserver._pyroTimeout = 30
sys.excepthook = Pyro4.util.excepthook

class Device(object):
    @staticmethod
    def run(args):
        proc = run(args, check=False, stdout=PIPE)
        proc.check_returncode()


class IrDevice(Device):
    @staticmethod
    def run(device,key,repeats=1):
        args = ["irsend","SEND_ONCE","--count=%s" % repeats,device,key]
        Device.run(args)


class HTPC(Device):
    awake = False

    @staticmethod
    def remotecall(func):
        if HTPC.awake:
            try:
                return func()
            except BaseException as e:
                # print("exception calling remote server")
                print("".join(Pyro4.util.getPyroTraceback()))

    @staticmethod
    def mouseaction(events):
        HTPC.remotecall(lambda: remoteserver.mouseaction(events))

    @staticmethod
    def keycombo(combo):
        HTPC.remotecall(lambda: remoteserver.keycombo(combo))

    @staticmethod
    def mute_app(appnames):
        for app in appnames:
            HTPC.remotecall(lambda: remoteserver.mute_app(app))

    @staticmethod
    def unmute_app(appnames):
        for app in appnames:
            HTPC.remotecall(lambda: remoteserver.unmute_app(app))

    @staticmethod
    def pause(appname):
        HTPC.remotecall(lambda: remoteserver.pause(appname))

    @staticmethod
    def stop_service(appname):
        HTPC.remotecall(lambda: remoteserver.pause_service(appname))

    @staticmethod
    def cont_service(appname):
        HTPC.remotecall(lambda: remoteserver.continue_service(appname))

    @staticmethod
    def wake():
        Device.run(["wol","00:1d:92:62:fd:19"])
        HTPC.awake = True

    @staticmethod
    def sleep():
        HTPC.remotecall(lambda: remoteserver.sleep())
        HTPC.awake = False

    def input(src):
        if src == KODI:
            keys = [e.KEY_LEFTMETA,e.KEY_1]
        elif src == SPOTIFY:
            keys = [e.KEY_LEFTMETA,e.KEY_2]
        elif src == WATCHPLAY:
            keys = [e.KEY_LEFTMETA,e.KEY_3]
        else:
            return
        HTPC.keycombo(keys)


class Tv(IrDevice):

    @staticmethod
    def command(cmd,repeats=1):
        IrDevice.run("lgtv",cmd,repeats)

    @staticmethod
    def poweron():
        IrDevice.run("lgtv","poweron")

    @staticmethod
    def poweroff():
        IrDevice.run("lgtv","poweroff")

    @staticmethod
    def channelup():
        IrDevice.run("lgtv","channelup")

    @staticmethod
    def channeldown():
        IrDevice.run("lgtv","channeldown")

    @staticmethod
    def input(src):
        IrDevice.run("lgtv",src)

class Receiver(IrDevice):

    @staticmethod
    def command(cmd,repeats=1):
        IrDevice.run("denonreceiver",cmd,repeats)

    @staticmethod
    def poweron():
        Receiver.command("poweron")

    @staticmethod
    def poweroff():
        Receiver.command("poweroff")

    @staticmethod
    def volumeup():
        Receiver.command("volumeup")

    @staticmethod
    def volumedown():
        Receiver.command("volumedown")

    @staticmethod
    def mute():
        Receiver.command("mute")

    @staticmethod
    def input(src):
        Receiver.command(src)

    @staticmethod
    def mode(mode):
        Receiver.command(mode)
