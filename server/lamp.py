import time
import sys
import RPi.GPIO as GPIO
from threading import Event

# Code pattern S TTTT TTTT TTTT TTTT TTTT TTTT TTGO CCUU P
# S: sync bit
# T: Transmitter id
# G: Group code, 0 for on, 1 for off
# O: On/off bit, 0 for on, 1 for off
# C: Channelbit nexa 11
# U: Unit #1 = 11, #2 = 10, #3 = 01.
# P: Pause bit
# Each code is sent 5 times for nexa

N = 5
T = 0.000210 # 175
TRANSMIT_PIN = 24
CHANNEL = '00'

SYNC_LOW = 10*T
ONE_LOW = 5*T
ZERO_LOW = T
PAUSE_LOW = 40*T

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRANSMIT_PIN, GPIO.OUT)

class Lamp(object):

    def __init__(self,transmitter_id, reciever_id):

        self.poweron = False
        self.dimon = False
        if reciever_id == 1:
            self.reciever_id = '11'
        elif reciever_id == 2:
            self.reciever_id = '01'
        elif reciever_id == 3:
            self.reciever_id = '10'
        bin_id = str(bin(transmitter_id))[2:]
        self.transmitter_id = (26-len(bin_id))*'0' + bin_id
        self.timer = Event()

    @property
    def is_on(self):
        return self.poweron

    def toggle(self):
        if self.dimon or not self.poweron:
            self.on()
            self.dimon = False
        else:
            self.off()

    def dim(self):
        if self.poweron:
            self.transmit('0','1')
            self.dimon = True

    def on(self):
        self.transmit('0','1')
        self.poweron = True

    def off(self):
        self.transmit('0','0')
        self.poweron = False

    def send_sync(self):
        self.send(T,SYNC_LOW)

    def send_pause(self):
        self.send(T,PAUSE_LOW)

    def send_bit(self,bit):
        if bit == '1':
            self.send(T,ONE_LOW)
            self.send(T,ZERO_LOW)
        elif bit == '0':
            self.send(T,ZERO_LOW)
            self.send(T,ONE_LOW)

    def ideal_time(self,code):
        sync_time = T + SYNC_LOW
        code_time = float(len(code))*(2*T+ONE_LOW+ZERO_LOW)
        pause_time = T + PAUSE_LOW
        return N*(sync_time + code_time + pause_time)*1000.0

    def send(self,t1,t2):
        GPIO.output(TRANSMIT_PIN,1)
        time.sleep(t1)
        GPIO.output(TRANSMIT_PIN,0)
        time.sleep(t2)

    def transmit(self,group,onoff):
        code = self.transmitter_id + group + onoff + CHANNEL + self.reciever_id
        code = code.replace(' ','')

        for n in range(N):
            self.send_sync()
            for i in code:
                self.send_bit(i)
            self.send_pause()


class LampGroup(Lamp):
    def __init__(self,lamps):
        self.lamps = lamps
        self.transmitter_id = self.get_transmitter_id()
        self.control_lamp = Lamp(int(self.transmitter_id,2),2)

    def toggle(self):
        if self.is_on():
            self.off()
        else:
            self.on()

    def on(self):
        self.control_lamp.transmit('1','1')
        for key, lamp in self.lamps.items():
            lamp.poweron = True

    def off(self):
        self.control_lamp.transmit('1','0')
        for key, lamp in self.lamps.items():
            lamp.poweron = False

    def is_on(self):
        for key,lamp in self.lamps.items():
            if lamp.is_on:
                return True
        return False

    def get_transmitter_id(self):
        transmitter_id = None
        for key, lamp in self.lamps.items():
            if transmitter_id and transmitter_id != lamp.transmitter_id:
                raise ValueError("Receiver id's not mathcing")
            else:
                transmitter_id = lamp.transmitter_id
        return transmitter_id

