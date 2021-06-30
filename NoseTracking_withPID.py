import cv2
import mediapipe as mp
import numpy as np
from djitellopy import Tello
from time import sleep


class NoseTracking():
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.cap = cv2.VideoCapture(0)
        self.w = 0
        self.h = 0
        self.c = 0
        self.cx = 0
        self.cy = 0
        self.landmark = [0, 8, 7, 13, 15, 14, 16, 11, 12]
        self.img = 0
        self.pError = 0
        self.pid = [0.2, 0.2, 0]
        self.posX_error = 0
        self.posY_error = 0
        self.speedX = 0
        self.speedY = 0
        self.id = None

        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth,
                                     self.detectionCon, self.trackCon)

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
        #success, img = cap.read()
        myFrame = cap.get_frame_read()
        #myFrame = myFrame.frame
        #self.img = cv2.resize(myFrame, (w, h))
        self.img = myFrame.frame

    def findPose(self, draw=False):
        """ This is for Webcam """
        #success, self.img = self.cap.read()

        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if draw:
            if self.results.pose_landmarks:
                self.mpDraw.draw_landmarks(self.img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)

    def findPosition(self):
        idList = []
        if self.results.pose_landmarks:
            for self.id, lm in enumerate(self.results.pose_landmarks.landmark):
                self.h, self.w, self.c = self.img.shape
                self.cx, self.cy = int(lm.x * self.w), int(lm.y * self.h)

                idList.append([self.id, self.cx, self.cy, self.w, self.h])
                self.detected = True

                # Draw Black Rectangle on bottom
                cv2.rectangle(self.img, (0, self.h-40), (self.w, self.h), (0, 0, 0), -1)

                # Draw Black Rectangle on top
                cv2.rectangle(self.img, (0, 0), (self.w, 50), (0, 0, 0), -1)

                if self.id in self.landmark:
                    cv2.circle(self.img, (self.cx, self.cy), 8, (0, 0, 255), cv2.FILLED)

        else:
            self.detected = False

        return idList

    def fancyDraw(self, post):
        # print(self.detected)

        if self.detected:
            if len(post) != 0 and post[0][0] == 0:
                # Draw Circle for middle image
                cv2.circle(self.img, (self.w // 2, self.h // 2), 5, (0, 255, 0), cv2.FILLED)

                # Draw Circle for nose image
                cv2.circle(self.img, (post[0][1], post[0][2]), 6, (0, 255, 0), cv2.FILLED)

                # Draw Arrow Line from Middle Image to Nose Image
                cv2.arrowedLine(self.img, (self.w // 2, self.h // 2),
                                (int(post[0][1]), int(post[0][2])), (255, 0, 255), 5, 10)

    def findPID(self, post, draw=True):

        if len(post) != 0 and post[0][0] == 0:

            if (post[15][2] < post[0][2]) and (post[16][2] > post[0][2]):
                cv2.putText(self.img, "Take Selfie", (self.w//2-100, 35),
                            cv2.FONT_HERSHEY_PLAIN, 2, (225, 255, 0), 2)

            elif (post[16][2] < post[0][2]) and (post[15][2] > post[0][2]):
                cv2.putText(self.img, "Landing", (self.w//2-50, 35),
                            cv2.FONT_HERSHEY_PLAIN, 2, (225, 255, 0), 2)
                self.myDrone.land()

            elif (post[16][2] > post[0][2]) and (post[15][2] > post[0][2]):
                cv2.putText(self.img, "Tracking", (self.w//2-70, 35),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            self.posX_error = post[0][1] - post[0][3]//2
            self.posY_error = post[0][2] - post[0][4]//2

            self.speedX = self.pid[0] * self.posX_error + \
                self.pid[1] * (self.posX_error - self.pError)
            self.speedY = self.pid[0] * self.posY_error + \
                self.pid[1] * (self.posY_error - self.pError)

            self.speedX = int(np.clip(self.speedX, -100, 100))
            self.speedY = int(np.clip(self.speedY, -100, 100))

            #print(post[0], self.posX_error, self.posY_error, self.speedX, self.speedY)

        if draw:
            # print(self.detected)
            if self.detected:
                self.myDrone.yaw_velocity = self.speedX
                self.myDrone.up_down_velocity = -self.speedY
                self.myDrone.left_right_velocity = 0
                self.myDrone.for_back_velocity = 15

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
    nose = NoseTracking()

    """ Tello Webcam """
    myDrone = nose.initialize()
    sleep(2)
    #myDrone.takeoff()
    #sleep(1)
    w, h = 640, 480

    while True:

        # Step 0 - Find Image From Tello Webcam
        img = nose.findImage(myDrone, w, h)

        # Step 1 - Find Pose
        nose.findPose()

        # Step 2 - Find position
        post = nose.findPosition()

        # Step 3 - FancyDraw
        draw = nose.fancyDraw(post)

        # Step 4 - Find PID
        nose.findPID(post)

        cv2.imshow("Results", nose.img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            nose.myDrone.land()
            sleep(1)
            break
    cv2.destroyAllWindows()
