# This example script demonstrates how use Python to allow users to send SDK to Tello commands with their keyboard
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/
# #####################
# send sequence of commands to test response speed


# Import the necessary modules
import socket
import threading
import time
from time import sleep
import sys

start_time = time.time()
# IP and port of Tello
tello_address = ('192.168.10.1', 8889)

# IP and port of local computer
#local_address = ('', 9000)  # switch to 8889 for same send/receive port?
local_address = ('', 8889)  # switch to 8889 for same send/receive port?

# Create a UDP connection that we'll send the command to
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind to the local address and port
sock.bind(local_address)

# Send the message to Tello and allow for a delay in seconds
def send(message):
  # Try to send the message otherwise print the exception
  try:
    sock.sendto(message.encode(), tello_address)
    print("Sending message: " + message)
    print("sent at time %f" % (time.time()-start_time))
  except Exception as e:
    print("Error sending: " + str(e))

# Receive the message from Tello
def receive():
  # Continuously loop and listen for incoming messages
  while True:
    # Try to receive the message otherwise print the exception
    try:
      response, ip_address = sock.recvfrom(128)
      print("Received message: " + response.decode(encoding='utf-8'))
      print("rcv'd at time %f" % (time.time()-start_time))
    except Exception as e:
      # If there's an error close the socket and break out of the loop
      sock.close()
      print("Error receiving: " + str(e))
      break
      
# Create and start a listening thread that runs in the background
# This utilizes our receive function and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

# Tell the user what to do
print('Type in a Tello SDK command and press the enter key. Enter "quit" to exit this program.')

# Loop infinitely waiting for commands or until the user types quit or ctrl-c
  
try:
   
    message='battery?'
    # Send the command to Tello
    send(message)
    sleep(0.2)
    message='temp?'
    # Send the command to Tello
    send(message)
    sleep(0.2)
    message='tof?'
    # Send the command to Tello
    send(message)
    sleep(0.2)
    print("Program exited sucessfully")
    sock.close()

    
  # Handle ctrl-c case to quit and close the socket
except KeyboardInterrupt as e:
    sock.close()
    print("Program exited after keybd interrupt")