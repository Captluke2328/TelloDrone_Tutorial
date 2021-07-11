from flask import  Flask, render_template, request, redirect, Response
import cv2
import threading
import keyboard as kp
from time import sleep
from djitellopy import Tello

class droneControlledWhistle():
    def __init__(self):
        self.app = Flask(__name__)
        self.data = None
        self.motion = None
        self.output = None
    
    def initDrone(self):
        self.myDrone = Tello()
        self.myDrone.connect()
        print(self.myDrone.get_battery())
        self.myDrone.streamon()

        return self.myDrone
    
    def run(self):
        @self.app.route('/', methods=['GET'])
        def show_index_html():
            self.app.logger.info('Load the html...')
            return render_template('index.html')
       
        @self.app.route('/', methods=['POST'])
        def get_data_from_html():
            self.data = request.form['audio']
            #self.classifyAudio()
            self.motion = self.data
            #("Audio command is " + self.data)
            return render_template('index.html')
            
        t = threading.Thread(target=self.app.run)
        t.start()

    def classifyAudio(self):
        lr, fb, ud, yv = 0,0,0,0
        speed = 50
        if self.motion == "Left":
            self.output = "Turn Left"
            lr = -speed

        elif self.motion == "Right":
            self.output = "Turn Right"
            lr = speed
        
    
        elif self.motion == "Forward":
            self.output = "Forward"
            fb = speed

        elif self.motion == "Backward":
            self.output = "Backward"
            fb = -speed

        elif self.motion == "Up":
            self.output = "Up"
            ud = speed
        
        elif self.motion == "Down":
            self.output = "Down"
            ud = -speed
            
        elif self.motion == "Stop":
            self.output = "Stop"
        
        elif self.motion == "Takeoff":
            self.output = "Takeoff"

        else:
            self.output = "Listening"
        
        return [self.output,lr,fb,ud,yv]

    def drawFancy(self,img,h,w,data):

        # Draw Black Rectangle on bottom
        cv2.rectangle(img, (0, h-40), (w, h), (0, 0, 0), -1)

        # Draw Black Rectangle on top
        cv2.rectangle(img, (0, 0), (w, 40), (0, 0, 0), -1)

        # Display Output on the top screen
        cv2.putText(img, data , (w//2-40, 35),cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        
        # Display Label on the bottom screen
        cv2.putText(img, "Whistle Controlled Drone" , (w//2-250, h-10),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
    
    def findImage(self, cap, w, h):
        #success, img = cap.read()
        myFrame = cap.get_frame_read()
        myFrame = myFrame.frame
        image = cv2.resize(myFrame, (w, h))
        return image

if __name__ == "__main__":
    
    cap = cv2.VideoCapture(0)

    listen = droneControlledWhistle()
    listen.run()
    
    #myDrone = listen.initDrone()
    

    w,h = 640,480
    
    while True:

        # Step 1 - Capture Image from Webcam
        success,img = cap.read()       
        #size = img.shape
        h = img.shape[0] #1280
        w = img.shape[1] #720
        #img = cv2.resize(img, (w,h))

        # Step 1 - Capture Image from Drone
        #img = listen.findImage(myDrone,w,h)
        
        # Step 2 - Listen to Audio and Set Drone Speed
        data = listen.classifyAudio()
        print(data)
      
        # Step 3 - Fly the drone
        #myDrone.send_rc_control(data[1], data[2], data[3], data[4])
        #sleep(0.05)
        
        # Step 3 - Draw Fancy
        listen.drawFancy(img,h,w,data[0])
    
        cv2.imshow("Output", img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

