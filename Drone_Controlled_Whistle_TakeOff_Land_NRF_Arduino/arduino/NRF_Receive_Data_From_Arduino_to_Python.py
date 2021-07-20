import serial
from time import sleep
from djitellopy import tello
import keyboard as kp

def initTello():
    try:
        me = tello.Tello()
        me.connect()
        print(me.get_battery())
    except:
        print("Connection Fail")

    return me

def initConnection(portNo, baudRate):
    try:
        ser = serial.Serial(portNo, baudRate)
        print("Device Connected")
        return ser

    except:
        print("Not connected")


def sendData(se, data, digits):
    myString="$"
    for d in data:
        myString += str(d).zfill(digits) #zfill - will fil the digit since we need 3 digits in this case
    try:
        se.write(myString.encode())
        print(myString)
    except:
        print("Data Transmission Failed")

def getData(ser):
    data = ser.readline()
    data = data.decode("utf-8")
    data = data.split("#")

    dataList = []
    [dataList.append(d) for d in data]
    return dataList[:-1]
    
def control(data, me):
    #print(int(data[1]))
    lr, fb, ud, yv = 0,0,0,0
    speed = 70
    
    if int(data[0]) == 130 and int(data[1]) == 129:
        status = "Listening"
    
    if int(data[0]) > 130:
        status = "Move Forward"
        fb = speed

    if int(data[0]) < 130:
        status = "Move Backward"
        fb = -speed

    if int(data[1]) > 129:
        status = "Move Right"
        lr = speed

    if int(data[1]) < 129:
        status = "Move Left"
        lr = -speed

    if kp.is_pressed('q'): me.land(); sleep(1)

    if kp.is_pressed('e'): me.takeoff()
    
    return [status,lr, fb, ud, yv]

if __name__ == "__main__":
    ser = initConnection("COM4", 9600)

    myDrone = initTello()
    while True:
        # Step 1 - Get Data from Arduino
        receiveData = getData(ser)

        # Step 2 - Extract Data from Arduino to Determine Motor Direction
        vals = control(receiveData, myDrone)

        myDrone.send_rc_control(vals[1], vals[2], vals[3], vals[4])

        # sendData(ser,[30,0],4)
        # sleep(1)
        # sendData(ser,[0,0],4)
        # sleep(1)

        #print(getData(ser))
        #print(getData(ser)[0])

        
