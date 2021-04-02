from PersonTrackingDrone_Function import *
from time import sleep

startCounter = 0

myDrone = initializeTello()

W,H = 640,480

pid = [0.3,0.2,0]
pError = 0

#cap = cv2.VideoCapture(0)
whT = 320

while True:

    ## Flight
    if startCounter == 0:
        myDrone.takeoff()
        myDrone.set_speed(50)
        startCounter = 1

    # Step 1
    img = findImage(myDrone, W, H)

    # Step 2
    info = findObject(img, whT, W, H)

    # Step 3
    if info != None:
        cx = info[0][0]
        area = info[1]
        pError = trackFace(myDrone, cx, area, W, pid, pError)
        print(area)
    else:
        pError = trackFace(myDrone, 0, 0,0, pid, pError)

    cv2.imshow("Tracking", img)
    if cv2.waitKey(1) & 0XFF==ord('q'):
        myDrone.land()
        sleep(1)
        break



