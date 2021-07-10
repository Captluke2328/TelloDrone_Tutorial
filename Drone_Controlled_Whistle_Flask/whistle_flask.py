from flask import  Flask, render_template, request, redirect, Response
import cv2
import threading, queue

class whistleFlask():
    def __init__(self):
        self.motion = None
        
    def capVideo(self):
        cap = cv2.VideoCapture(0)
        while True:
            success,self.img = cap.read()
            cv2.putText(self.img, str(self.classifyAudio) ,cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 3)
            cv2.imshow("Output", self.img)
            if cv2.waitKey(1) & 0XFF == ord('q'):
                break

    def classifyAudio(self,data):
        lr, fb, ud, yv = 0,0,0,0
        self.motion = data
        speed = 50
        if self.motion == "Left":
            print("Turn Left") 
            lr = -speed

        elif self.motion == "Right":
            print("Turn Right")
            lr = speed
        
        elif self.motion == "Stop":
            print("Land")
        
        elif self.motion == "Takeoff":
            print("Takeoff")
        
        elif self.motion == "Forward":
            print("Move Forward")
            fb = speed

        elif self.motion == "Backward":
            print("Move Backward")
            fb = -speed

        elif self.motion == "Up":
            print("Move Up")
            lr = speed
        
        elif self.motion == "Down":
            print("Move Down")
         
        print(lr,fb)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def show_index_html():
    app.logger.info('Load the html...')
    return render_template('index.html')

@app.route('/', methods=['POST'])
def get_data_from_html():
    data = request.form['audio']

    init = whistleFlask()
    init.classifyAudio(data)

    print("Audio command is " + data)
    return render_template('index.html')

def main():    
    app.run(threaded=True)

if __name__ == "__main__":  
    init = whistleFlask()

    process_thread = threading.Thread(target=main)
    process_thread.daemon=True
    process_thread.start()

    img_thread = threading.Thread(target=init.capVideo())
    img_thread.daemon=True
    img_thread.start()

    #whistleFlask.capVideo()

    # Method 2
    # t1 = threading.Thread(target=main, args=[])
    # #t2 = threading.Thread(target=capVideo, args=[])
    # t1.start()
    # #t1.join()
    # #t2.start()
    # capVideo()