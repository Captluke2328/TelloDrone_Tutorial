import cv2
import numpy as np
from djitellopy import Tello
import time

confThreshold = 0.5
nms_threshold = 0.3

classNames = []
classesFile = r'E:\Python Project\Resources\AI_Files\Yolo_v3\coco.names'
modelConfiguration = r'E:\Python Project\Resources\AI_Files\Yolo_v3\yolov3-tiny.cfg'
modelWeights = r'E:\Python Project\Resources\AI_Files\Yolo_v3\yolov3-tiny.weights'

with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('\n').rsplit('\n')

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
fbRange = [6200, 6800]

def initializeTello():
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

def findImage(cap, W, H):
    #success, img = cap.read()
    myFrame = cap.get_frame_read()
    myFrame = myFrame.frame
    img = cv2.resize(myFrame, (W, H))
    
    # Draw Middle Line
    cv2.line(img, (W // 2, 0), (W // 2, H), (0, 255, 0), 3)
    return img

def findObject(img, whT, W, H):
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (whT, whT), [0, 0, 1], 1, crop=False)
    net.setInput(blob)
    LayerNames = net.getLayerNames()
    outputNames = [LayerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)

    hT, wT, cT = img.shape
    boundingbox = []
    classIds = []
    confidenceLevel = []
    myObjectListC = []
    myObjectListArea = []

    for output in outputs:
        for detect in output:
            scores = detect[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]

            if confidence > confThreshold:
                w, h = int(detect[2] * wT), int(detect[3] * hT)
                x, y = int((detect[0] * wT) - w / 2), int((detect[1] * hT - h / 2))
                boundingbox.append([x, y, w, h])
                classIds.append(classId)
                confidenceLevel.append(float(confidence))
        indices = cv2.dnn.NMSBoxes(boundingbox, confidenceLevel, confThreshold, nms_threshold)

    for i in indices:
        i = i[0]
        box = boundingbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        cx = x + (w // 2)
        cy = y + (h // 2)
        area = w * h

        # Draw Middle Object to the middle Line
        cv2.line(img, (W // 2, cy), (cx, cy), (0, 255, 0), 3)
        # Draw Circle in the middle of the object
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        # Draw Rectangle line on the detected object
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)
        cv2.putText(img, f'{classNames[classIds[i]].upper()} {int(confidenceLevel[i] * 100)}%', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        myObjectListArea.append(area)
        myObjectListC.append([cx, cy])

        if len(myObjectListArea) != 0:
            if (f'{classNames[classIds[i]].upper()}') == 'PERSON':
                i = myObjectListArea.index(max(myObjectListArea))
                return [myObjectListC[i], myObjectListArea[i]]
            else:
                return [[0, 0], 0]
        else:
            return [[0, 0], 0]


def trackFace(myDrone, cx, area, W, pid, pError):
    error = cx - W // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -60, 60))

    if cx != 0:
        if area < fbRange[1]:
            myDrone.yaw_velocity = speed
            myDrone.for_back_velocity = 20
        
        else:
            myDrone.yaw_velocity = 0
            myDrone.for_back_velocity = 0

    else:
        myDrone.for_back_velocity = 0
        myDrone.left_right_velocity = 0
        myDrone.up_down_velocity = 0
        myDrone.yaw_velocity = 0
        error = 0

    if myDrone.send_rc_control:
        myDrone.send_rc_control(myDrone.left_right_velocity,
                                myDrone.for_back_velocity,
                                myDrone.up_down_velocity,
                                myDrone.yaw_velocity)

    return speed
