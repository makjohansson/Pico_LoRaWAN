from lib.lorawan import LoRaWAN
from lib.config import Keys
import utime
'''
Example sending the value 10 in hex(0A) every 20 seconds
'''
lora = LoRaWAN(Keys['DevEUI'], Keys['AppEUI'], Keys['AppKey'])
lora.led(1)
#lora.reset() # uncomment to reset RAK811 and rejoin
if not lora.has_joined:
    while not lora.has_joined:
        lora.join()
    print('Network joined')

print('Network ready')

while True:
    lora.send('0A')
    lora.sleep()
    utime.sleep(20)
    lora.wake_up()
    utime.sleep(1)




