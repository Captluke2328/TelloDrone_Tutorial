import cv2

cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    fps = cap.get(cv2.CAP_PROP_FPS)

    cv2.putText(img, str(fps), (40,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0),3)
    cv2.imshow("Result",img)
    if cv2.waitKey(1) & 0XFF == ord('q'):
        break