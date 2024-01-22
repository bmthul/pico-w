import network, array, time
import socket
import rp2
from time import sleep
from machine import Pin,PWM, RTC

ssid = 'avm7360'
password = '7955743501919411thul'

website = """<!DOCTYPE html>
<html>
    <head> <title>Raspberry Pi Pico W</title> </head>
    <style>
       label{width:120px; display:inline-block}
    </style>
    <body>
        <h1>controll leds</h1>
        <p><label>Kanal 1</label><input type='button' value='toggle' onclick='toggleLed("gelb")'/>
        <label> Kanal 1 Aus</label><input type='button' value='toggle' onclick='toggleLed("geaus")'/>
        <p><label>Kanal 2</label><input type='button' value='toggle' onclick='toggleLed("blau")'/>
        <label>Kanal 2 Aus</label><input type='button' value='toggle' onclick='toggleLed("blaus")'/>
        <br/>
        <p><label>Kanal 3</label><input type='button' value='toggle' onclick='toggleLed("gruen")'/>
        <label>Kanal 3 Aus</label><input type='button' value='toggle' onclick='toggleLed("graus")'/>
        <br/>
        <p><label>Kanal 4</label><input type='button' value='toggle' onclick='toggleLed("rot")'/>
        <label>Kanal 4 Aus</label><input type='button' value='toggle' onclick='toggleLed("raus")'/>
        <br/>
        <p><label>Kanal 5</label><input type='button' value='toggle' onclick='toggleLed("fuenf")'/>
        <label>Kanal 5 Aus</label><input type='button' value='toggle' onclick='toggleLed("faus")'/>
        <br/>
        <p><label>Kanal 6</label><input type='button' value='toggle' onclick='toggleLed("sechs")'/>
        <label>Kanal 6 Aus</label><input type='button' value='toggle' onclick='toggleLed("seaus")'/>
        <br/>
        <p><label>Kanal 7</label><input type='button' value='toggle' onclick='toggleLed("sieben")'/>
        <label>Kanal 7 Aus</label><input type='button' value='toggle' onclick='toggleLed("siaus")'/>
        <br/>
        <p><label>Kanal 8</label><input type='button' value='toggle' onclick='toggleLed("acht")'/>
        <label>Kanal 8 Aus</label><input type='button' value='toggle' onclick='toggleLed("acaus")'/>
        <br/>
        
        <script>
            function toggleLed(led){
                var xhttp = new XMLHttpRequest();
                xhttp.open('GET', '/led/'+led, true);
                xhttp.send();
            }
        </script>
    </body>
</html>
"""

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
    
max_wait = 10
print('Warte auf Verbindung')
while max_wait > 10:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1    
    sleep(1)

status = None
if wlan.status() != 3:
    raise RuntimeError('Aufbau der Verbindung fehlgeschlagen!')
else:
    status = wlan.ifconfig()
    print('Verbindung zu', ssid,'erfolgreich aufgebaut!', sep=' ')
    print('IP-Adresse: ' + status[0])

ipAddress = status[0]

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

NUM_LEDS = 1
PIN_NUM = 13
pwm = PWM(Pin(6))
pwm.freq(1000)

rtc = RTC()
datetime = rtc.datetime()


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
class NeoPixel(object):
    def __init__(self,pin=PIN_NUM,num=NUM_LEDS,brightness=0.8):
        self.pin=pin
        self.num=num
        self.brightness = brightness
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num)])   
        self.ch1 = Pin(21,Pin.OUT)
        self.ch2 = Pin(20,Pin.OUT)
        self.ch3 = Pin(19,Pin.OUT)
        self.ch4 = Pin(18,Pin.OUT)
        self.ch5 = Pin(17,Pin.OUT)
        self.ch6 = Pin(16,Pin.OUT)
        self.ch7 = Pin(15,Pin.OUT)
        self.ch8 = Pin(14,Pin.OUT)
    ##########################################################################

    def Relay_CHx(self,n,switch): 
        if switch == 1:
            n.high()
        else:
            n.low()
            
strip = NeoPixel()
while True:
    try:
        cl, addr = s.accept()
        print('Verbindung vom Client ', addr, "angenommen!")
        request = cl.recv(1024)
        request = str(request)
        
        req_state_led_gelb = request.find('/led/gelb') == 6
        req_state_led_geaus = request.find('/led/geaus') == 6
        req_state_led_blau = request.find('/led/blau') == 6
        req_state_led_blaus = request.find('/led/blaus') == 6
        req_state_led_gruen = request.find('/led/gruen') == 6
        req_state_led_graus = request.find('/led/graus') == 6
        req_state_led_rot = request.find('/led/rot') == 6
        req_state_led_raus = request.find('/led/raus') == 6
        req_state_led_fuenf = request.find('/led/fuenf') == 6
        req_state_led_faus = request.find('/led/faus') == 6
        req_state_led_sechs = request.find('/led/sechs') == 6
        req_state_led_seaus = request.find('/led/seaus') == 6
        req_state_led_sieben = request.find('/led/sieben') == 6
        req_state_led_siaus = request.find('/led/siaus') == 6
        req_state_led_acht = request.find('/led/acht') == 6
        req_state_led_acaus = request.find('/led/acaus') == 6

        if req_state_led_gelb == True:
           strip.Relay_CHx(strip.ch1,1)
           print("1A")
        if req_state_led_geaus == True:
           strip.Relay_CHx(strip.ch1,0)
           print("1B")
        if req_state_led_blau == True:
           strip.Relay_CHx(strip.ch2,1)
           print("2A")
        if req_state_led_blaus == True:
           strip.Relay_CHx(strip.ch2,0)
           print("2B")
        if req_state_led_gruen == True:
           strip.Relay_CHx(strip.ch3,1)
           print("3A")
        if req_state_led_graus == True:
           strip.Relay_CHx(strip.ch3,0)
           print("3B")
        if req_state_led_rot == True:
           strip.Relay_CHx(strip.ch4,1)
           print("4A")
        if req_state_led_raus == True:
           strip.Relay_CHx(strip.ch4,0)
           print("4B")
        if req_state_led_fuenf == True:
           strip.Relay_CHx(strip.ch5,1)
           print("5A")
        if req_state_led_faus == True:
           strip.Relay_CHx(strip.ch5,0)
           print("5B")
        if req_state_led_sechs == True:
           strip.Relay_CHx(strip.ch6,1)
           print("6A")
        if req_state_led_seaus == True:
           strip.Relay_CHx(strip.ch6,0)
           print("6B")
        if req_state_led_sieben == True:
           strip.Relay_CHx(strip.ch7,1)
           print("7A")
        if req_state_led_siaus == True:
           strip.Relay_CHx(strip.ch7,0)
           print("7B")
        if req_state_led_acht == True:
           strip.Relay_CHx(strip.ch8,1)
           print("8A")
        if req_state_led_acaus == True:
           strip.Relay_CHx(strip.ch8,0)
           print("8B")

 
           
        html = website
       
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
