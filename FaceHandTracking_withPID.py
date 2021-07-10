import cv2
import mediapipe as mp
import time
import numpy as np
from djitellopy import Tello
from time import sleep

class faceDetectionCustom():
    def __init__(self, mode=False, detection=0.5, trackCon=0.5,maxHands=1):
        self.cap = cv2.VideoCapture(0)
        self.mode = mode
        self.detectionCon = detection
        self.trackCon = trackCon
        self.tipIds = [4, 8, 12, 16, 20]

        """Face"""
        self.mFace = mp.solutions.face_detection

        """Hand """
        self.maxHands = maxHands
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
    
        self.speedRightLeft = 0
        self.speedForwardBackWard = 0
        self.pTime = 0
        self.cTime = 0
        self.l = 30
        self.t = 10
        self.posX_error = 0
        self.posY_error = 0
        self.speedX = 0
        self.speedY = 0
        self.speedRightLeft = 0
        self.speedForwardBackward = 0
        self.pXError = 0
        self.pYError = 0
        self.pid = [0.2, 0.2, 0]
        self.cx = 0
        self.cy = 0
        self.width = 0
        self.height = 0
        self.area = 0
        self.bbox = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.x1 = 0
        self.y1 = 0

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

    def findImage(self, cap, w, h):
        #success, image = cap.read()
        myFrame = cap.get_frame_read()
        myFrame = myFrame.frame
        self.image = cv2.resize(myFrame, (w, h))

    def findNoseHand(self, draw=False, NoseDetect=True, HandDetect=True): 
        success, self.image = self.cap.read()
        imageRGB = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.resultsHand = self.hands.process(imageRGB)

        if HandDetect:
            if self.resultsHand.multi_hand_landmarks:
                for handLms in self.resultsHand.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(self.image, handLms, self.mpHands.HAND_CONNECTIONS)

    def faceHandPosition(self,draw= True, FacePost= True, HandPost = True, HandNo = 0):
        lhList = []
        with self.mFace.FaceDetection(min_detection_confidence=0.5) as face:       
            self.image.flags.writeable = True
            myAreaList = []
            imageRGB = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.resultsHand = self.hands.process(imageRGB)

            results = face.process(imageRGB)

            if results.detections:
                if FacePost:
                    for self.detections in results.detections:
                        for id, lm in enumerate(results.detections):
                            bboxC = lm.location_data.relative_bounding_box
                            self.height, self.width, centre = self.image.shape
                            self.bbox = int(bboxC.xmin * self.width), int(bboxC.ymin * self.height), int(
                                bboxC.width * self.width), int(bboxC.height * self.height)

                            # Locate Centre Detected Face Image
                            self.detected = True
                            self.x, self.y, self.w, self.h = self.bbox
                            self.cx = self.x + self.w // 2
                            self.cy = self.y + self.h // 2
                            self.area = self.w * self.h
                            self.x1, self.y1 = self.x + self.w, self.y + self.h

                if HandPost:
                    if self.resultsHand.multi_hand_landmarks:
                        myHand = self.resultsHand.multi_hand_landmarks[HandNo]
                        for id, lm in enumerate(myHand.landmark):
                            h,w,c = self.image.shape
                            cx,cy = int(lm.x*w), int(lm.y*h)
                        
                            lhList.append([id, cx, cy])

                            if draw:
                                cv2.circle(self.image, (cx,cy), 3,(255,0,255),cv2.FILLED)
                
                    # Draw Black Rectangle on bottom
                    cv2.rectangle(self.image, (0, self.height-40), (self.width, self.height), (0, 0, 0), -1)

                    # Draw Black Rectangle on top
                    cv2.rectangle(self.image, (0, 0), (self.width, 40), (0, 0, 0), -1)

            else:
                self.detected = False
                self.speedX = 0
                self.speedY = 0
                self.cx = 0
                self.cy = 0

            self.cTime = time.time()
            fps = 1/(self.cTime - self.pTime)
            self.pTime = self.cTime

            cv2.putText(self.image, str(int(fps)), (10, 37),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            return lhList

    def fancyDraw(self):
        if self.detected:
            # cv2.line(self.image, (self.w // 2, 0), (self.w // 2, self.h), (0, 255, 0), 3)

            # Draw circle in the middle of the image
            cv2.circle(self.image, (self.width // 2, self.height // 2), 8, (0, 0, 255), cv2.FILLED)

            # Draw circle in the middle of the face image
            cv2.circle(self.image, (self.cx, self.cy), 8, (0, 0, 255), cv2.FILLED)

            # Draw line for middle face image to middle image
            cv2.line(self.image, (self.width//2, self.height//2),
                     (int(self.cx), int(self.cy)), (255, 0, 255), 3)

            # Draw BBOX
            cv2.rectangle(self.image, self.bbox, (255, 0, 255), 2)
            #cv2.putText(self.image, f'{int(self.detections.score[0] * 100)}%', (self.bbox[0], self.bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

            # Top Left x,y
            cv2.line(self.image, (self.x, self.y), (self.x + self.l, self.y), (255, 0, 255), self.t)
            cv2.line(self.image, (self.x, self.y), (self.x, self.y + self.l), (255, 0, 255), self.t)

            # Top Right x1,y
            cv2.line(self.image, (self.x1, self.y),
                     (self.x1 - self.l, self.y), (255, 0, 255), self.t)
            cv2.line(self.image, (self.x1, self.y),
                     (self.x1, self.y + self.l), (255, 0, 255), self.t)

            # Bottom Left x,y1
            cv2.line(self.image, (self.x, self.y1),
                     (self.x + self.l, self.y1), (255, 0, 255), self.t)
            cv2.line(self.image, (self.x, self.y1),
                     (self.x, self.y1 - self.l), (255, 0, 255), self.t)

            # Bottom Right x1,y1
            cv2.line(self.image, (self.x1, self.y1),
                     (self.x1 - self.l, self.y1), (255, 0, 255), self.t)
            cv2.line(self.image, (self.x1, self.y1),
                     (self.x1, self.y1 - self.l), (255, 0, 255), self.t)

    def findPID(self,info, draw=False):
        if len(info) !=0:
            fingers = []
            # Check for Thumb CX position
            if(info[self.tipIds[0]][1]) < (info[self.tipIds[0]-1][1]):
                fingers.append(1)
            else:
                fingers.append(0)
            
            # Check for other Finger CY Position
            for id in range(1,5):
                #print(post[1][self.tipIds[id]][2])
                if(info[self.tipIds[id]][2]) < (info[self.tipIds[id]-2][2]):
                    fingers.append(1)
                else:
                    fingers.append(0)

            self.totalFingers = fingers.count(1)
            #print(fingers)
            if fingers == [0,1,0,0,0]:
                self.command = "Flip"
                #myDrone.flip()

            if fingers == [1,1,0,0,0]:
                self.command = "Left"
                self.speedRightLeft = 30
                self.speedForwardBackward = 0
                 
            elif fingers == [1,0,0,0,1]:
                self.command = "Right"
                self.speedRightLeft = -30
                self.speedForwardBackward = 0
            
            elif fingers == [1,1,1,0,0]:
                self.command = "Forward" 
                self.speedRightLeft = 0
                self.speedForwardBackward = 30

            elif fingers == [1,1,1,1,1]:
                self.command = "Backward"
                self.speedRightLeft = 0
                self.speedForwardBackward = -20

            elif fingers == [1,1,0,0,1]:
                self.command = "Stop"
                #self.myDrone.land()
            
            else:
                self.command = "Tracking"
                self.speedRightLeft = 0
                self.speedForwardBackward = 0
        else:
            self.command = "Tracking"
            self.speedRightLeft = 0
            self.speedForwardBackward = 0

        self.posX_error = self.cx - self.width//2
        self.posY_error = self.cy - self.height//2

        self.speedX = self.pid[0] * self.posX_error + self.pid[1] * (self.posX_error - self.pXError)
        self.speedY = self.pid[0] * self.posY_error + self.pid[1] * (self.posY_error - self.pYError)

        self.speedX = int(np.clip(self.speedX, -100, 100))
        self.speedY = int(np.clip(self.speedY, -100, 100))

        self.pXError = self.posX_error
        self.pYError = self.posX_error
        
        cv2.putText(self.image, self.command, (self.width//2-40, 35),cv2.FONT_HERSHEY_PLAIN, 2, (225, 255, 0), 2)
        cv2.putText(self.image, "Speed: " + str(self.speedX), (self.width//2-60, self.height-10),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        print(self.command)
        
        #print(self.posX_error, self.posY_error, self.speedX, self.speedY)

        if draw:
            #print(self.posX_error, self.posY_error, self.speedX, self.speedY)
            if self.detected:
                self.myDrone.yaw_velocity = self.speedX
                self.myDrone.up_down_velocity = -self.speedY
                self.myDrone.left_right_velocity = self.speedRightLeft
                self.myDrone.for_back_velocity = self.speedForwardBackward

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
    face = faceDetectionCustom()

    """ Tello Webcam """
    #myDrone = face.initialize()
    #sleep(2)
    #myDrone.takeoff()
    sleep(1)
    w, h = 640, 480
    while True:

        # Step 0 - Find Image From Tello Webcam
        #image = face.findImage(myDrone,w,h)

        face.findNoseHand()

        # Step 1 - Detect Face
        info = face.faceHandPosition()

        # Step 2 - Draw Image
        draw = face.fancyDraw()

        # Step 2 - Calculate Speed
        droneSpeed = face.findPID(info)

        image = cv2.resize(face.image, (1020, 720))
        cv2.imshow("Image Detection", image)

        if cv2.waitKey(1) & 0XFF == ord('q'):
            face.myDrone.land()
            sleep(1)
            break
    cv2.destroyAllWindows()
