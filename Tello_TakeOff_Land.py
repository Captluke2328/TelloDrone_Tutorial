import time

from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()
starCounter = 0

print(me.get_battery())

while True:
    if starCounter == 0:
        me.takeoff()
        sleep(1)
        me.land()
    starCounter = 1





