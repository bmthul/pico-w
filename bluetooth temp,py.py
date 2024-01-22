from machine import Pin, ADC
import bluetooth
import time
from ble_simple_peripheral import BLESimplePeripheral
from dht import DHT22

# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()
sp = BLESimplePeripheral(ble)

# Initialisierung des ADC4
sensor = ADC(4)
conversion_factor = 3.3 / (65535)
dht22_sensor = DHT22(Pin(27, Pin.IN, Pin.PULL_UP))


# Wiederholung einleiten (Schleife)
while True:
   dht22_sensor.measure()
   if sp.is_connected():
    dht22_sensor.measure()
    # Werte lesen
    temp = dht22_sensor.temperature()
    humi = dht22_sensor.humidity()
    feuchte= 'Luftfeuchtigkeit:' + str(humi) + '%'
    sp.send(str(feuchte).encode() + "\n")
    temperatur = 'Temperatur: ' + str(temp) + ' Cel'
    sp.send(str(temperatur).encode() + "\n")
    # 2 Sekunden warten
   time.sleep(10)