import threading
import socket
import time

"""
Tello IP Address. Use local IP address since host/computer is a WiFi client to Tello
"""
tello_ip = "192.168.10.1"

"""
Tello port to send command message
"""
command_port = 8889

"""
Host IP Address. 0.0.0.0 is referring to current host/computer IP address
"""
host_ip = "0.0.0.0"

"""
UDP port to receive response msg from Tello.
Tello command response will be communicated using this port
"""
response_port = 9000

""" Welcome Note"""
print("\nTello Command Program\n")

class Tello:
    def __init__(self):
        self._running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host_ip,response_port))

    def terminate(self):
        self._running = False
        self.sock.close()

    def recv(self):
        """Handler for Tello response Message"""
        while self._running:
            try:
                msg, _ = self.sock.recvfrom(1024)
                print("response: {}".format(msg.decode(encoding="utf-8")))
            except Exception as err:
                print(err)

    def send(self, msg):
        """ Handler for send message to Tello """
        msg = msg.encode(encoding="utf-8")
        self.sock.sendto(msg, (tello_ip, command_port))
        print("message: {}".format(msg))  # Print message

""" Start new thread for receive Tello response message """
t = Tello()
recvThread = threading.Thread(target=t.recv)
recvThread.start()

while True:
    try:
        # Get input from CLI
        msg = input()
        t.send(msg)

        # Check for "end"
        if msg == "bye":
            t.terminate()
            recvThread.join()
            print("\nGood Bye\n")
            break
    except KeyboardInterrupt:
        t.terminate()
        recvThread.join()
        break