from subprocess import run, PIPE
from time import sleep
import sys
import traceback
import json
import Pyro4
from evdev import ecodes as e
import logging as log

from config import *

remoteserver = Pyro4.Proxy("PYRONAME:zteifel.remoteserver@192.168.1.69:9093")
remoteserver._pyroTimeout = 25
sys.excepthook = Pyro4.util.excepthook

class Device(object):
    @staticmethod
    def run(args):
        proc = run(args, check=False, stdout=PIPE, stderr=PIPE)
        if proc.returncode != 0:
            log.error('Command %s failed with errorcode: %i \n Error: %s' %
                      (' '.join(args),proc.returncode), proc.stderr)


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
                result = func()
                if result and result[1] != 0:
                    err_msg = (
                        'The remote call: %s failed with msg:' % result[0],
                        result[2],
                        result[3])
                    log.error('\n'.join(err_msg))
            except Exception as e:
                log.error(e)
                traceback = '\n'.join(Pyro4.util.getPyroTraceback())
                log.error('Failed remote call: %s' % traceback)

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
        # Device.run(["wake-htpc"])
        HTPC.awake = True
        log.debug('Waking up HTPC')

    @staticmethod
    def sleep():
        # HTPC.remotecall(lambda: remoteserver.sleep())
        HTPC.awake = False
        log.debug('Putting HTPC to sleep')

    def input(src):
        log.debug('Swithcing HTPC input to %s' % src)
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
        log.debug('Turning on TV')

    @staticmethod
    def poweroff():
        IrDevice.run("lgtv","poweroff")
        log.debug('Turning off TV')

    @staticmethod
    def channelup():
        IrDevice.run("lgtv","channelup")

    @staticmethod
    def channeldown():
        IrDevice.run("lgtv","channeldown")

    @staticmethod
    def input(src):
        IrDevice.run("lgtv",src)
        log.debug('Switching TV input to %s' % src)

class Receiver(IrDevice):

    @staticmethod
    def command(cmd,repeats=1):
        IrDevice.run("denonreceiver",cmd,repeats)

    @staticmethod
    def poweron():
        log.debug('Turning on receiver')
        Receiver.command("poweron")

    @staticmethod
    def poweroff():
        Receiver.command("poweroff")
        log.debug('Turning off reciever')

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
        log.debug('Switching receiver input to %s' % src)

    @staticmethod
    def mode(mode):
        Receiver.command(mode)
