# Bibliotheken laden
import machine
import network
import sys
import time
import usocket as socket
import ustruct as struct
from machine import Pin,SPI,PWM,RTC
import framebuf
import usocket as socket
import ustruct as struct


wlanSSID = 'Suzi'
wlanPW = 'samirgiebel11'
# network.country('DE')
Dot       = 0x80

# Winterzeit / Sommerzeit
GMT_OFFSET = 3600 * 1 # 3600 = 1 h (Winterzeit)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (Sommerzeit)

# Status-LED
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# NTP-Host
NTP_HOST = 'pool.ntp.org'

# Funktion: WLAN-Verbindung
def wlanConnect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('WLAN-Verbindung herstellen')
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            print('.')
            time.sleep(1)
    if wlan.isconnected():
        print('WLAN-Verbindung hergestellt / WLAN-Status:', wlan.status())
        led_onboard.on()
    else:
        print('Keine WLAN-Verbindung')
        led_onboard.off()
        print('WLAN-Status:', wlan.status())

# Funktion: Zeit per NTP holen
def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)

# Funktion: RTC-Zeit setzen
def setTimeRTC():
    # NTP-Zeit holen
    tm = getTimeNTP()
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

# WLAN-Verbindung herstellen
wlanConnect()

# Zeit setzen
setTimeRTC()

# Aktuelles Datum ausgeben
SEG8Code = [
    0x3F, # 0
    0x06, # 1
    0x5B, # 2
    0x4F, # 3
    0x66, # 4
    0x6D, # 5
    0x7D, # 6
    0x07, # 7
    0x7F, # 8
    0x6F, # 9
    0x77, # A
    0x7C, # b
    0x39, # C
    0x5E, # d
    0x79, # E
    0x71  # F
    ] 
class LED_8SEG():
    def __init__(self):
        self.rclk = Pin(9,Pin.OUT)
        self.rclk(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(10),mosi=Pin(11),miso=None)
        self.SEG8=SEG8Code
    '''
    MOSI = 11
    SCK = 10    
    RCLK = 9
    function: Send Command
    parameter: datetime = rtc.datetime()
        Num: bit select
        Seg：segment select       
    Info:The data transfer
    '''
    def write_cmd(self, Num, Seg):    
        self.rclk(1)
        self.spi.write(bytearray([Num]))
        self.spi.write(bytearray([Seg]))
#       print(Seg)
        self.rclk(0)
#        time.sleep(0.5)
#        self.rclk(1)

rtc = RTC()
datetime = machine.RTC().datetime()
if __name__=='__main__':
    LED = LED_8SEG()
    #color BRG
    while(1):
            datetime = machine.RTC().datetime()
            stunde=str(datetime[4])
            if len(str(datetime[4]))<2:
               stunde="0"+stunde 
            minute=str(datetime[5])
            if len(str(datetime[5]))<2:
               minute="0"+minute
            r1=int(stunde[0:1])
            r2=int(stunde[1:2])
            r3=int(minute[0:1])
            r4=int(minute[1:2])
            LED.write_cmd(247,LED.SEG8[r4])
            time.sleep(0.5)
            LED.write_cmd(251,LED.SEG8[r3])
            time.sleep(0.5)
            LED.write_cmd(253,LED.SEG8[r2]|Dot)
            time.sleep(0.5)
            LED.write_cmd(254,LED.SEG8[r1])
            time.sleep(0.5)