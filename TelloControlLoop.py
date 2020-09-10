# ToDo
# 1. add thread for state information
# 2. add timestamp time.time()
#  sleep(0.100) try commands every 0.1 sec
# 3. write state information to file
# 4. try speed or other command to see what loop time is
#5. write commands to file with time stamp as well.
#6. can data be merged across threads?
 # https://www.pythonforthelab.com/blog/handling-and-sharing-data-between-threads/
# maybe use queue?
 #  # float(data[1].split(':')[1])
 
 # state format string:
 # b'mid:64;x:0;y:0;z:0;mpry:0,0,0;pitch:-3;roll:-7;yaw:87;vgx:0;vgy:0;vgz:0;
# templ:80;temph:82;tof:10;h:0;bat:80;baro:218.46;time:13;agx:-67.00;agy:125.00;agz:-992.00;\r\n'
 # convert string to nuber, map?
 # .find?
 # b'mid:64; x:0; y:0; z:0 ;mpry:0,0,0; pitch:-3; roll:-7; yaw:87; vgx:0;vgy:0;vgz:0;
 # 0          1    2    3      4         5          6         7     8     9      10
# templ:80;temph:82;tof:10; h:0; bat:80; baro:218.46; 
 # 11       12      13      14    15      16
# time:13; agx:-67.00; agy:125.00; agz:-992.00;\r\n'
#   17      18          19           20
# This example script demonstrates how use Python to allow users to send SDK to Tello commands with their keyboard
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/

# Import the necessary modules
import socket
import threading
import time
from time import sleep
import sys

INTERVAL = 0.2  # update rate for state information

# IP and port of Tello for commands
tello_address = ('192.168.10.1', 8889)
# IP and port of local computer
local_address = ('', 9000)
# Create a UDP connection that we'll send the command to
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to the local address and port
sock.bind(local_address)

###################
# socket for state information
#local_port = 8890
#socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
#socket.bind(('', local_port))
#socket.sendto('command'.encode('utf-8'), tello_address)   # command port on Tello


# place holder for generating telemetry file
def report(str):
#    stdscr.addstr(0, 0, str)
#    stdscr.refresh()
    print(str)

# Send the message to Tello and allow for a delay in seconds
def send(message):
  # Try to send the message otherwise print the exception
  try:
    sock.sendto(message.encode(), tello_address)
    print("Sending message: " + message)
  except Exception as e:
    print("Error sending: " + str(e))

# receive state message from Tello
def rcvstate():
    index = 0
    while not stateStop.is_set():
        index += 1
        response, ip = socket.recvfrom(1024)
        if response == 'ok':
            continue
 # .replace formatting gives error in python 3?
 #           out = response.replace(';', ';\n')
        out = 'Tello State:\n' + str(response)
        report(out)
        sleep(INTERVAL)
    print('finished rcvstate thread')

# Receive the message from Tello
def receive():
  # Continuously loop and listen for incoming messages
  while True:
    # Try to receive the message otherwise print the exception
    try:
      response, ip_address = sock.recvfrom(128)
      print("Received message: " + response.decode(encoding='utf-8'))
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

stateThread = threading.Thread(target=rcvstate)
stateThread.daemon = False  # want clean file close
stateStop = stateThread.event
stateStop.clear()
stateThread.start()


# Tell the user what to do
print('Type in a Tello SDK command and press the enter key. Enter "quit" to exit this program.')

# Loop infinitely waiting for commands or until the user types quit or ctrl-c
while True:
  
  try:
    # Read keybord input from the user
    if (sys.version_info > (3, 0)):
      # Python 3 compatibility
      message = input('')
    else:
      # Python 2 compatibility
      message = raw_input('')
    
    # If user types quit then lets exit and close the socket
    if 'quit' in message:
      print("Program exited")
      sock.close()  # sockete for commands
      socket.close()  # socket for state
      stateStop.set()  # set stop variable
      stateThread.join()   # wait for termination of state thread
      print("sockets and threads closed")
      # send message
      
      break
    
    # Send the command to Tello
    send(message)
    
  # Handle ctrl-c case to quit and close the socket
  except KeyboardInterrupt as e:
    sock.close()
    break