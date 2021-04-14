from time import sleep
from KeyboardControl_Surveillance_Function import *
import threading, queue
import cv2

myDrone = initializeTello()
whT = 320
W,H = 640,480

def getKeyboardInput():
    lr, fb, ud, yv = 0,0,0,0
    speed = 80

    if kp.is_pressed('LEFT'): lr = -speed

    elif kp.is_pressed('RIGHT'): lr = speed

    if kp.is_pressed('UP'): fb = speed

    elif kp.is_pressed('DOWN'): fb = -speed

    if kp.is_pressed('w'):ud = speed

    elif kp.is_pressed('s'): ud = -speed

    if kp.is_pressed('a'):yv = -speed

    elif kp.is_pressed('d'): yv = speed

    if kp.is_pressed('q'): myDrone.land(); sleep(1)

    if kp.is_pressed('e'): myDrone.takeoff()

    return [lr, fb, ud, yv]

def readkeyboard():
    ## Read Keyboard Key
    #q = queue.Queue()
    #threading.Thread(target=getKeyboardInput).start()
    #vals = q.get()
    vals = getKeyboardInput()
    myDrone.send_rc_control(vals[0], vals[1], vals[2], vals[3])

while True:
    ## Stream Image
    img = findImage(myDrone, W, H)
    info = findObject(img, whT, W, H)
    
    readkeyboard()
    
    cv2.imshow("Tracking", img)
    if cv2.waitKey(1) & 0XFF==ord('q'):
        myDrone.land()
        sleep(1)
        break

