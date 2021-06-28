import cv2
import mediapipe as mp
import time

class faceDetectionCustom():
    def __init__(self):
        self.cap    = cv2.VideoCapture(0)
        self.mFace  = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.pTime  = 0
        self.cTime  = 0
        self.l      = 30
        self.t      = 10

    def faceDetections(self):
        with self.mFace.FaceDetection(min_detection_confidence=0.5) as face:
            while True:
                success,self.image = self.cap.read()
                self.image.flags.writeable = True

                imgRGB = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                results = face.process(imgRGB)

                if results.detections:
                    for self.detections in results.detections:
                        for id,lm in enumerate (results.detections):
                            bboxC = lm.location_data.relative_bounding_box
                            h,w,c = self.image.shape
                            self.bbox = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)

                            self.fancyDraw()

                self.cTime = time.time()
                fps = 1/(self.cTime - self.pTime)
                self.pTime = self.cTime

                cv2.putText(self.image, str(int(fps)), (10, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                cv2.imshow("Image Detection", self.image)

                if cv2.waitKey(1) & 0XFF == ord('q'):
                    break

    def fancyDraw(self):
        x,y,w,h = self.bbox
        x1,y1 = x +w, y+h
        cv2.rectangle(self.image, self.bbox, (255, 0, 255), 2)
        cv2.putText(self.image, f'{int(self.detections.score[0] * 100)}%', (self.bbox[0], self.bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
        # cv2.line(image, (w // 2, 0), (w // 2, h), (0, 255, 0), 3)

        # Top Left x,y
        cv2.line(self.image, (x,y), (x + self.l, y), (255,0,255),self.t)
        cv2.line(self.image, (x,y), (x ,y + self.l), (255,0,255),self.t)

        # Top Right x1,y
        cv2.line(self.image, (x1, y), (x1 - self.l, y), (255, 0, 255), self.t)
        cv2.line(self.image, (x1, y), (x1, y + self.l), (255, 0, 255), self.t)

        # Bottom Left x,y1
        cv2.line(self.image, (x, y1), (x + self.l, y1), (255, 0, 255), self.t)
        cv2.line(self.image, (x, y1), (x, y1 - self.l), (255, 0, 255), self.t)

        # Bottom Right x1,y1
        cv2.line(self.image, (x1, y1), (x1 - self.l, y1), (255, 0, 255), self.t)
        cv2.line(self.image, (x1, y1), (x1, y1 - self.l), (255, 0, 255), self.t)

if __name__ == "__main__":
    face = faceDetectionCustom()

    faceDetection = face.faceDetections()
