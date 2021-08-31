from djitellopy import Tello
import PS4Joystick as js
from time import sleep

movement = 'Joystick'
me = Tello()
me.connect()
print(me.get_battery())

def move():
    flag = 0
    if movement == 'Joystick':
        jsVal = js.getJS()
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 70

        if flag == 0:
            if (jsVal['o']) == 1:
                me.takeoff()
                print("Take off")
                sleep(1)
                flag = 1

        if(jsVal['t']) == 1:
            me.land()
            print("Land")
            flag = 0
            sleep(1)

        if(jsVal['axis1']) == 1:
            lr = speed#"right"

        elif (jsVal['axis1']) == -1.0:
            lr = -speed#"left"

        if (jsVal['axis2']) == 1:
            fb = -speed #"backward"

        elif (jsVal['axis2']) == -1.0:
            fb = speed #"forward"

        if (jsVal['axis3']) == 1:
            yv = speed #"pitchright"

        elif (jsVal['axis3']) == -1.0:
            yv = -speed #"pitchleft"

        if (jsVal['axis4']) == 1:
            ud = -speed #"down"

        elif (jsVal['axis4']) == -1.0:
            ud = speed #"up"

        if(jsVal['axis1']) !=1 and (jsVal['axis1']) !=-1 and (jsVal['axis2']) != 1 and (jsVal['axis2']) != -1 and (jsVal['axis3']) != 1 and (jsVal['axis3']) != -1 and (jsVal['axis4']) != 1 and (jsVal['axis4']) != -1:
            lr, fb, ud, yv = 0,0,0,0

        return [lr,fb,ud,yv]

if __name__ == '__main__':
    while True:
        vals = move()
        print(vals)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])