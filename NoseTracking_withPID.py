import cv2
import mediapipe as mp
import numpy as np
from djitellopy import Tello


class NoseTracking():
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.cap = cv2.VideoCapture(0)
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth,
                                     self.detectionCon, self.trackCon)

    def findPose(self):
        success, self.img = self.cap.read()
        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if results.pose_landmarks:
            self.mpDraw.draw_landmarks(self.img, self.results.pose_landmarks,
                                       self.mpPose.POSE_CONNECTIONS)

    def findPosition(self):
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = self.img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(self.img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

\


if __name__ == "__main__":
    nose = NoseTracking()

    while True:
        # Step 1 - Find Pose
        nose.findPose()

        # Step 2 - Find position
        nose.findPosition()

        cv2.imshow("Results", nose.img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break
