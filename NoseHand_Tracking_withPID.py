import cv2
import mediapipe as mp
import numpy as np
from time import sleep
from djitellopy import Tello

class NoseHandTracking():
    def __init__(self, mode=False, upBody=False, smooth=True, detection=0.5, trackCon=0.5,maxHands=1):
        self.cap = cv2.VideoCapture(0)
        self.landmark = [0, 7, 8]
        self.img = 0
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detection
        self.trackCon = trackCon

        self.tipIds = [4, 8, 12, 16, 20]
        self.h = 0
        self.w = 0
        self.c = 0
        self.cx = 0
        self.cy = 0
        self.pError = 0
        self.pid = [0.2, 0.2, 0]
        self.posX_error = 0
        self.posY_error = 0
        self.speedX = 0
        self.speedY = 0
        
        """Init Nose"""
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

        """Init Hand"""
        self.maxHands = maxHands
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
    
    def initialize(self):
        self.myDrone = Tello()
        self.myDrone.connect()
        self.myDrone.for_back_velocity = 0
        self.myDrone.left_right_velocity = 0
        self.myDrone.up_down_velocity = 0
        self.myDrone.yaw_velocity = 0
        self.myDrone.speed = 0
        print(self.myDrone.get_battery())
        self.myDrone.streamoff()
        self.myDrone.streamon()
        return self.myDrone

    def findNoseHand(self, draw=False, NoseDetect=True, HandDetect=True): 
        """ This is for Webcam """
        #success,self.img = self.cap.read() 

        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.resultsNose = self.pose.process(imgRGB)
        self.resultsHand = self.hands.process(imgRGB)

        if NoseDetect:      
            if draw:
                if self.resultsNose.pose_landmarks:
                    self.mpDraw.draw_landmarks(self.img, self.resultsNose.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        
        if HandDetect:
            if self.resultsHand.multi_hand_landmarks:
                for handLms in self.resultsHand.multi_hand_landmarks:
                    #if draw:
                    self.mpDraw.draw_landmarks(self.img, handLms, self.mpHands.HAND_CONNECTIONS)

    def findPosition(self,draw=True,NosePost=True,HandPost=True,handNo=0):
        lnList = []
        lhList = []

        if self.resultsNose.pose_landmarks:
            if NosePost:
                if self.resultsNose.pose_landmarks:
                    for id, lm in enumerate(self.resultsNose.pose_landmarks.landmark):
                        self.h,self.w,self.c = self.img.shape
                        self.cx,self.cy = int(lm.x * self.w), int(lm.y * self.h)
                        
                        lnList.append([id,self.cx,self.cy,self.w,self.h])
                        self.detected = True
                        
                        if id in self.landmark:
                            cv2.circle(self.img, (self.cx,self.cy), 8, (0,0,255),cv2.FILLED)
            if HandPost:
                if self.resultsHand.multi_hand_landmarks:
                    myHand = self.resultsHand.multi_hand_landmarks[handNo]
                    for id, lm in enumerate(myHand.landmark):
                        h,w,c = self.img.shape
                        cx,cy = int(lm.x*w), int(lm.y*h)
                        
                        lhList.append([id, cx, cy])

                        if draw:
                            cv2.circle(self.img, (cx,cy), 3,(255,0,255),cv2.FILLED)
            
                # Draw Black Rectangle on bottom
                cv2.rectangle(self.img, (0, self.h-40), (self.w, self.h), (0, 0, 0), -1)

                # Draw Black Rectangle on top
                cv2.rectangle(self.img, (0, 0), (self.w, 40), (0, 0, 0), -1)
        else:
            self.detected = False
        
        return [lnList,lhList]

    def findImage(self, cap, w, h):
        #success, img = cap.read()
        myFrame = cap.get_frame_read()
        myFrame = myFrame.frame
        self.img = cv2.resize(myFrame, (w, h))

    def fancyDraw(self, post):
            #print(self.detected)
            if self.detected:
                if len(post[0]) != 0 and post[0][0][0] == 0:
                    # Draw Circle for middle image
                    cv2.circle(self.img, (self.w // 2, self.h // 2), 5, (0, 255, 0), cv2.FILLED)

                    # Draw Circle for nose image
                    cv2.circle(self.img, (post[0][0][1], post[0][0][2]), 6, (0, 255, 0), cv2.FILLED)

                    # Draw Arrow Line from Middle Image to Nose Image
                    cv2.arrowedLine(self.img, (self.w // 2, self.h // 2),
                                    (int(post[0][0][1]), int(post[0][0][2])), (255, 0, 255), 5, 10)        

    def findPID(self,post, draw=True):
        if len(post[0]) !=0 and post[0][0][0] == 0:
            if len(post[1]) !=0:
                fingers = []

                if(post[1][self.tipIds[0]][1]) < (post[1][self.tipIds[0]-1][1]):
                    #print(post[1][self.tipIds[1]])
                    fingers.append(1)
                else:
                    fingers.append(0)
                
                for id in range(1,5):
                    #print(post[1][self.tipIds[id]][2])
                    if(post[1][self.tipIds[id]][2]) < (post[1][self.tipIds[id]-2][2]):
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                self.totalFingers = fingers.count(1)
                #print(self.totalFingers)
                #print(fingers)
                
                if fingers == [0,1,0,0,0]:
                    self.command = "Flip"

                if fingers == [1,1,0,0,0]:
                    self.command = "Left"
                
                elif fingers == [1,0,0,0,1]:
                    self.command = "Right"
                
                elif fingers == [1,1,1,0,0]:
                    self.command = "Forward"

                elif fingers == [1,1,1,1,1]:
                    self.command = "Backward"

                elif fingers == [1,1,0,0,1]:
                    self.command = "Stop"
                
                else:
                    self.command = "Tracking"

            else:
                self.command = "Tracking"

            #print(post[1][self.tipIds[id]])

            self.posX_error = post[0][0][1] - self.w//2
            self.posY_error = post[0][0][1] - self.h//2

            self.speedX = self.pid[0] * self.posX_error + self.pid[1] * (self.posX_error - self.pError)
            self.speedY = self.pid[0] * self.posY_error + self.pid[1] * (self.posY_error - self.pError)

            self.speedX = int(np.clip(self.speedX, -100, 100))
            self.speedY = int(np.clip(self.speedY, -100, 100))
  
        if draw:
            if self.detected:
                self.myDrone.yaw_velocity = self.speedX
                self.myDrone.up_down_velocity = -self.speedY
                self.myDrone.left_right_velocity = 0
                self.myDrone.for_back_velocity = 15

                print(self.speedX,self.command)

                cv2.putText(self.img, self.command, (self.w//2-40, 35),cv2.FONT_HERSHEY_PLAIN, 2, (225, 255, 0), 2)
                cv2.putText(self.img, "Speed: " + str(self.speedX), (self.w//2-60, self.h-10),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            else:
                self.myDrone.for_back_velocity = 0
                self.myDrone.left_right_velocity = 0
                self.myDrone.up_down_velocity = 5
                self.myDrone.yaw_velocity = 0

            if self.myDrone.send_rc_control:
                self.myDrone.send_rc_control(self.myDrone.left_right_velocity,
                                            self.myDrone.for_back_velocity,
                                            self.myDrone.up_down_velocity,
                                            self.myDrone.yaw_velocity)

if __name__ == "__main__":
    detect = NoseHandTracking()

    """ Tello Webcam """
    myDrone = detect.initialize()
    sleep(2)
    #myDrone.takeoff()
    #sleep(1)
    w,h = 640,480

    while True:
        
        # Step 0 - Find Image From Tello Webcam
        img = detect.findImage(myDrone, w, h)

        # Step 1 - Find Nose
        detect.findNoseHand()

        # Step 2 - Find Position
        post = detect.findPosition()
        
        # Extract Hand List
        #if len(post[1]) !=0:
        #    print(post[1])

        # Extract Nose List
        #if len(post[0]) !=0:
        #    print(post[0][0])

        # Step 3 - FancyDraw
        draw = detect.fancyDraw(post)

        # Step 4 - Track
        speed = detect.findPID(post)

        cv2.imshow("Streaming", detect.img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            #nose.myDrone.land()
            sleep(1)
            break
    cv2.destroyAllWindows()
    
