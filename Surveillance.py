from djitellopy import tello
import keyboard as kp
from time import sleep
import cv2

me = tello.Tello()
me.connect()

print(me.get_battery())
me.streamon()

def getKeyboardInput():
    lr, fb, ud, yv = 0,0,0,0
    speed = 50

    if kp.is_pressed('LEFT'): lr = -speed

    elif kp.is_pressed('RIGHT'): lr = speed

    if kp.is_pressed('UP'): fb = speed

    elif kp.is_pressed('DOWN'): fb = -speed

    if kp.is_pressed('w'):ud = speed

    elif kp.is_pressed('s'): ud = -speed

    if kp.is_pressed('a'):yv = -speed

    elif kp.is_pressed('d'): yv = speed

    if kp.is_pressed('q'): me.land(); sleep(1)

    if kp.is_pressed('e'): me.takeoff()

    return [lr, fb, ud, yv]

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)

    img = me.get_frame_read().frame
    img = cv2.resize(img,(360,240))
    cv2.imshow("Image", img)
    cv2.waitKey(1)