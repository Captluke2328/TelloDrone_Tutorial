from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()

print(me.get_battery())
me.takeoff()
#me.send_rc_control(0,50,0,0) #left right velocity, forward back velocity, up down velocity,yaw velocity
#sleep(2)
#me.send_rc_control(0,0,0,30)
#sleep(2)
#me.send_rc_control(0,0,0,0)
#me.land()

### ---- Another Method ---- ###
me.send_rc_control(0,0,0,50) #left right velocity, forward back velocity, up down velocity,yaw velocity
sleep(2)
me.send_rc_control(0,0,0,-50)
sleep(2)
me.send_rc_control(0,0,0,0)
me.land()