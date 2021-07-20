import threading
import cv2
from flask import  Flask, render_template, request, redirect, Response
from djitellopy import Tello
from time import sleep
import serial
import sys
import concurrent.futures
# if sys.version > '3':
# 	import queue as Queue
# else:
# 	import Queue

class whistleTakeoffLand():
    def __init__(self):
        self.app = Flask(__name__)
        self.data = None
        self.cap = cv2.VideoCapture(0)
        self.motion = None
        self.output = None
        self.startCounter = 0

    def findImage(self, cap, w, h):
        # success, img = cap.read()
        myFrame = cap.get_frame_read()
        myFrame = myFrame.frame
        image = cv2.resize(myFrame, (w, h))
        return image

    def run(self):
        @self.app.route('/', methods=['GET'])
        def show_index_html():
            self.app.logger.info('Load the html...')
            return render_template('index.html')

        @self.app.route('/', methods=['POST'])
        def get_data_from_html():
            self.data = request.form['audio']
            self.motion = self.data
            return render_template('index.html')

        t = threading.Thread(target=self.app.run)
        t.start()

    def classifyAudio(self,data,myDrone):
        lr, fb, ud, yv = 0,0,0,0
        speed = 70

        if self.motion == "Takeoff":
            if self.startCounter == 0:
                self.output = "Takeoff"
                myDrone.takeoff()
                self.startCounter = 1

        #self.startCounter = 1
        if self.startCounter == 1:
            if self.motion == "Land":
                self.output = "Land"
                myDrone.land()
                self.startCounter = 0
        
            if int(data[0]) == 130 and int(data[1]) == 129:
                self.output = "Listening"

            if int(data[0]) > 130:
                self.output = "Move Forward"
                fb = speed

            if int(data[0]) < 130:
                self.output = "Move Backward"
                fb = -speed

            if int(data[1]) > 129:
                self.output = "Move Right"
                lr = speed

            if int(data[1]) < 129:
                self.output = "Move Left"
                lr = -speed

            else:
                self.output = "Listening"

        return [self.output, lr, fb, ud, yv]

    def drawFancy(self, img, h, w, data):
        # Draw Black Rectangle on bottom
        cv2.rectangle(img, (0, h - 40), (w, h), (0, 0, 0), -1)

        # Draw Black Rectangle on top
        cv2.rectangle(img, (0, 0), (w, 40), (0, 0, 0), -1)

        # Display Output on the top screen
        cv2.putText(img, data, (w // 2 - 40, 35), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)

        # Display Label on the bottom screen
        cv2.putText(img, "Whistle Controlled Drone", (w // 2 - 200, h - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

    def findImagex(self,cap):
        success, img = cap.read()
        return img

    def initDrone(self):
        try:
            myDrone = Tello()
            myDrone.connect()
            print(myDrone.get_battery())
            myDrone.streamon()
        except:
            print("Not connected")

        return myDrone
            
    def initConnection(self,portNo, baudRate):
        try:
            ser = serial.Serial(portNo, baudRate)
            print("Device Connected")
            return ser

        except:
            print("Not connected")

    def getData(self,ser):
        data = ser.readline()
        data = data.decode("utf-8")
        data = data.split("#")

        dataList = []
        [dataList.append(d) for d in data]
        return dataList[:-1]

with concurrent.futures.ThreadPoolExecutor() as executor:
    if __name__ == "__main__":
        
        listen = whistleTakeoffLand()
        listen.run()

        ser = listen.initConnection("COM4", 9600)
        myDrone = listen.initDrone()

        w,h = 640,480
        
        while True:   
            # Step 0 - Get Data from Arduino
            receiveData = listen.getData(ser)
            #f1 = executor.submit(listen.getData,ser)    
            #receiveData =f1.result()

            # Step 1 - Capture Image from Webcam
            #success, img = listen.cap.read()
            # h = img.shape[0]  # 1280
            # w = img.shape[1]  # 720
            #f2 = executor.submit(listen.findImagex,listen.cap)
            #img = f2.result()

            # Step 1 - Capture Image from Drone
            #img = listen.findImage(myDrone,w,h)

            # Step 3 - Listen to Audio and Set Drone Speed
            data = listen.classifyAudio(receiveData,myDrone)
            #print(data)
            
            # Step 4 - Draw Fancy
            #listen.drawFancy(img, h, w, data[0])

            # Step 5 - Fly Drone
            myDrone.send_rc_control(data[1], data[2], data[3], data[4])
            #sleep(0.05)

            # cv2.imshow("Output",img)
            # if cv2.waitKey(1) & 0XFF == ord('q'):
            #     #myDrone.land()
            #     break



