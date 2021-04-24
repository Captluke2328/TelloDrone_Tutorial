import cv2
import mediapipe as mp
import time
import numpy as np
from djitellopy import Tello


class poseDetectionModule():
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def initialize(self):
        myDrone = Tello()
        myDrone.connect()
        myDrone.for_back_velocity = 0
        myDrone.left_right_velocity = 0
        myDrone.up_down_velocity = 0
        myDrone.yaw_velocity = 0
        myDrone.speed = 0
        print(myDrone.get_battery())
        myDrone.streamoff()
        myDrone.streamon()
        return myDrone

    def drawLine(self, img, w, h):
        cv2.line(img, (w // 2, 0), (w // 2, h), (0, 255, 0), 3)
        cv2.line(img, (0, h // 2), (w, h // 2), (0, 255, 0), 3)
        return img

    def findImage(self, cap, w, h):
        # success, img = cap.read()
        myFrame = cap.get_frame_read()
        myFrame = myFrame.frame
        img = cv2.resize(myFrame, (w, h))
        return img

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy, w, h])
                if draw:
                    cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)
        return self.lmList

    def findPID(self, img, lmList, pid, pError, detected, myDrone, draw=True):
        speedRightLeft = 0
        speedForwardBackward = 0
        """Detect Nose and Track"""
        if len(lmList[0]) != 0 & lmList[0][0] == 0:
            if (lmList[16][2] > lmList[12][2]) & (lmList[15][2] > lmList[11][2]):
                speedRightLeft = 0
                speedForwardBackward = 0

            # """Detect Nose, Right Arm, Shoulders and Track, Move Right"""
            #if lmList[0][0] == 0:
            if (lmList[16][2] < lmList[12][2]) & (lmList[15][2] > lmList[11][2]):
                print("Right arm is up")
                speedRightLeft = -30
                speedForwardBackward = 0

            """Detect Nose, Left Arm, Shoulders and Track, Move Left"""
            #if lmList[0][0] == 0:
            if (lmList[15][2] < lmList[11][2]) & (lmList[16][2] > lmList[12][2]):
                print("Left arm is up")
                speedRightLeft = 30
                speedForwardBackward = 0

            """Detect Nose, Right Elbow, Shoulder and Track, Move Forward"""
            if (lmList[19][2] < lmList[11][2]) & (lmList[15][2] > lmList[11][2]):
                print("Move Forward")
                speedRightLeft = 0
                speedForwardBackward = 40

            """Detect Nose, Left Elbow, Shoulder and Track, Move Backward"""
            if (lmList[20][2] < lmList[12][2]) & (lmList[16][2] > lmList[12][2]):
                print("Move Backward")
                speedRightLeft = 0
                speedForwardBackward = -30

            """Detect Nose, Left Arm, Right Arm, Shoulder and Track, Stop"""
            if (lmList[16][2] < lmList[12][2]) & (lmList[15][2] < lmList[11][2]):
                print("Stop")
                myDrone.land()

            posX_error = lmList[0][1] - lmList[0][3] // 2
            posY_error = lmList[0][2] - lmList[0][4] // 2

            speedX = pid[0] * posX_error + pid[1] * (posX_error - pError)
            speedY = pid[0] * posY_error + pid[1] * (posY_error - pError)

            speedX = int(np.clip(speedX, -100, 100))
            speedY = int(np.clip(speedY, -100, 100))

        if detected:
            if lmList[0][1] != 0 | lmList[0][2] != 0:
                print(speedX,-speedY, speedRightLeft)
                myDrone.yaw_velocity = speedX
                myDrone.up_down_velocity = -speedY
                myDrone.left_right_velocity = speedRightLeft
                myDrone.for_back_velocity = speedForwardBackward

            else:
                myDrone.for_back_velocity = 0
                myDrone.left_right_velocity = 0
                myDrone.up_down_velocity = 30
                myDrone.yaw_velocity = 0

            if myDrone.send_rc_control:
                myDrone.send_rc_control(myDrone.left_right_velocity,
                                        myDrone.for_back_velocity,
                                        myDrone.up_down_velocity,
                                        myDrone.yaw_velocity)
        return speedX

    def Scanning(self, detected, speed):
        if detected == False:
            myDrone.up_down_velocity = speed
            myDrone.send_rc_control(myDrone.left_right_velocity,
                                    myDrone.for_back_velocity,
                                    myDrone.up_down_velocity,
                                    myDrone.yaw_velocity)
            print(0, speed)


def main():
    """Webcam"""
    cap = cv2.VideoCapture(0)

    detector = poseDetectionModule()
    w, h = 640, 480
    pid = [0.1, 0.1, 0]
    pError = 0
    speed = 30
    startCounter = 0

    """Tello Webcam Return"""
    #return detector,w,h,pid,pError,speed, startCounter

    """WebCam Return"""
    return cap, detector, w, h, pid, pError, speed, startCounter

if __name__ == "__main__":

    """Tello WebCam"""
    #detector,  w, h, pid, pError, speed, startCounter = main()

    """WebCam"""
    cap, detector, w, h, pid, pError, speed, startCounter = main()

    myDrone = detector.initialize()
    myDrone.takeoff()
    while True:

        #if startCounter == 0:
        #    myDrone.takeoff()
        #    time.sleep(1)
        #startCounter = 1

        success, img = cap.read()

        ## Step 0 - Find Image from Tello WebCam
        #img = detector.findImage(myDrone, w,h)

        ## Step 1 -Detect Pose
        img = detector.findPose(img)

        ## Step 2 - Find Position
        lmList = detector.findPosition(img)

        ## Step 3 - Draw Line
        img = detector.drawLine(img, w, h)

        ## Step 3 - Find PID speed
        if len(lmList) != 0:
            detected = True
            position = detector.findPID(img, lmList, pid, pError, detected, myDrone)

        # else:
        # myDrone.up_down_velocity = speed
        # myDrone.yaw_velocity = 0
        # myDrone.send_rc_control(myDrone.left_right_velocity,
        #                        myDrone.for_back_velocity,
        #                        myDrone.up_down_velocity,
        #                        myDrone.yaw_velocity)

        cv2.imshow("Result", img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            myDrone.land()
            time.sleep(1)
            break
cv2.destroyAllWindows()
