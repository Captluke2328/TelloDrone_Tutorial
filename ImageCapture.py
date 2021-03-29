from djitellopy import tello
import cv2

VS_UDP_IP = '0.0.0.0'
VS_UDP_PORT = 11111

#cv2.VideoCapture('udp://@' + str(VS_UDP_IP) + ':' + str(VS_UDP_PORT))

me = tello.Tello()

me.connect()

print(me.get_battery())

me.streamon()

while True:
    img = me.get_frame_read().frame
    height, width, _ = img.shape

    new_h = int(height / 2)
    new_w = int(width / 2)

    # Resize for improved performance
    new_frame = cv2.resize(img, (new_w, new_h))

    #img = cv2.resize(img, (360, 240))
    cv2.imshow("Image", new_frame)
    cv2.waitKey(1)



