import threading
import cv2
from flask import  Flask, render_template, request, redirect, Response
from djitellopy import Tello
from time import  sleep
class whistleTakeoffLand():
    def __init__(self):
        #self.cap = cv2.VideoCapture(0)
        self.app = Flask(__name__)
        self.data = None
        self.motion = None
        self.output = None
        self.startCounter = 0

    def initDrone(self):
        try:
            self.myDrone = Tello()
            self.myDrone.connect()
            print(self.myDrone.get_battery())
            self.myDrone.streamon()
        except:
            print("Not connected")
        return self.myDrone

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

    def classifyAudio(self):
        lr, fb, ud, yv = 0,0,0,0
        speed = 50
        if self.motion == "Takeoff":

            if self.startCounter == 0:
                self.output = "Takeoff"
                self.myDrone.takeoff()
                sleep(0.1)
                self.startCounter = 1
        else:
            self.output = "Listening"
            lr, fb, ud, yv = 0, 0, 0, 0

        if self.startCounter == 1:
            if self.motion == "Land":
                self.output = "Land"
                self.myDrone.land()
                #self.myDrone.flip_forward()
                self.startCounter = 0
                #ud = -speed
        else:
            self.output = "Listening"
            lr, fb, ud, yv = 0, 0, 0, 0

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

if __name__ == "__main__":
    listen = whistleTakeoffLand()
    listen.run()

    myDrone = listen.initDrone()
    w,h = 640,480
    while True:

        # Step 1 - Capture Image from Webcam
        # success, img = listen.cap.read()
        # h = img.shape[0]  # 1280
        # w = img.shape[1]  # 720

        # Step 1 - Capture Image from Drone
        img = listen.findImage(myDrone,w,h)

        # Step 2 - Listen to Audio and Set Drone Speed
        data = listen.classifyAudio()
        print(data)

        # Step 3 - Draw Fancy
        listen.drawFancy(img, h, w, data[0])

        # Step 4 - Fly Drone
        myDrone.send_rc_control(data[1], data[2], data[3], data[4])
        # sleep(0.05)

        cv2.imshow("Output",img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            myDrone.land()
            break



