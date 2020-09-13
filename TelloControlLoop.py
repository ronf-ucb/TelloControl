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
 # convert string to nubmer, map?
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
import numpy as np
from queue import Queue


State_data_file_name = 'statedata.txt'
index = 0
control_input = 0 # command being sent to tello
INTERVAL = 0.05  # update rate for state information
start_time = time.time()
dataQ = Queue()

# IP and port of Tello for commands
tello_address = ('192.168.10.1', 8889)
# IP and port of local computer
local_address = ('', 8889)
# Create a UDP connection that we'll send the command to
CmdSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CmdSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind to the local address and port
CmdSock.bind(local_address)

###################
# socket for state information
local_port = 8890
StateSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
StateSock.bind(('', local_port))
CmdSock.sendto('command'.encode('utf-8'), tello_address)   # command port on Tello

def writeFileHeader(dataFileName):
    fileout = open(dataFileName,'w')
    #write out parameters in format which can be imported to Excel
    today = time.localtime()
    date = str(today.tm_year)+'/'+str(today.tm_mon)+'/'+str(today.tm_mday)+'  '
    date = date + str(today.tm_hour) +':' + str(today.tm_min)+':'+str(today.tm_sec)
    fileout.write('"Data file recorded ' + date + '"\n')
# header information
    fileout.write('index,    time,   control, mid,x ,y, z, mp, mr, my, pitch, roll, \
                  yaw, vgx, vgy, vgz, templ, temph, tof, h,bat,baro,time,agx,agy,agz\n\r')
    fileout.close()

def writeDataFile(dataFileName):
    fileout = open(State_data_file_name, 'a')  # append
    print('writing data to file')
    while not dataQ.empty():
        telemdata = dataQ.get()
        np.savetxt(fileout , [telemdata], fmt='%7.2f', delimiter = ',')  # need to make telemdata a list
    fileout.close()



def report(str,index):
#    stdscr.addstr(0, 0, str)
#    stdscr.refresh()
    telemdata=[]
    telemdata.append(index)
    telemdata.append(time.time()-start_time)
    telemdata.append(control_input) # ok if single input, otherwise need to synchronise
    data = str.split(';')
    data.pop() # get rid of last element, which is \\r\\n
    for value in data:
        temp = value.split(':')
        if temp[0] == 'mpry':    # roll/pitch/yaw
            temp1 = temp[1].split(',')
            telemdata.append(float(temp1[0]))     # roll
            telemdata.append(float(temp1[1]))     # pitch
            telemdata.append(float(temp1[2]))     # yaw
            continue
        quantity = float(value.split(':')[1])
        telemdata.append(quantity)
    dataQ.put(telemdata)
    if (index %100) == 0:
        print(index, end=',')
 
    

# Send the message to Tello and allow for a delay in seconds
def send(message):
  # Try to send the message otherwise print the exception
  try:
    CmdSock.sendto(message.encode(), tello_address)
    print("Sending message: " + message)
  except Exception as e:
    print("Error sending: " + str(e))

# receive state message from Tello
def rcvstate():
    print('Started rcvstate thread')
    index = 0
    while not stateStop.is_set():
        
        response, ip = StateSock.recvfrom(1024)
        if response == 'ok':
            continue
 # .replace formatting gives error in python 3?
 #           out = response.replace(';', ';\n')
        # out = 'Tello State:\n' + str(response)
        report(str(response),index)
        sleep(INTERVAL)
        index +=1
    print('finished rcvstate thread')

# Receive the message from Tello
def receive():
  # Continuously loop and listen for incoming messages
  while True:
    # Try to receive the message otherwise print the exception
    try:
      response, ip_address = CmdSock.recvfrom(128)
      print("Received message: " + response.decode(encoding='utf-8'))
    except Exception as e:
      # If there's an error close the socket and break out of the loop
      CmdSock.close()
      print("Error receiving: " + str(e))
      break

      

# Create and start a listening thread that runs in the background
# This utilizes our receive function and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

stateThread = threading.Thread(target=rcvstate)
stateThread.daemon = False  # want clean file close
stateStop = threading.Event()
stateStop.clear()
stateThread.start()
writeFileHeader(State_data_file_name)

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
      CmdSock.close()  # sockete for commands
      stateStop.set()  # set stop variable
      stateThread.join()   # wait for termination of state thread before closing socket
      StateSock.close()  # socket for state  
      writeDataFile(State_data_file_name)
      print("sockets and threads closed")
      # send message
      
      break
    
    # Send the command to Tello
    send(message)
    sleep(1.0) # wait for takeoff and motors to spin up
    for i in range(0,4):
        message='cw 30' # 10 degrees
        control_input = 30
        send(message)
        sleep(0.5)
        message='ccw 30' # -10 degrees
        control_input = -30
        send(message)
        sleep(0.5)
    message='ccw 1' # -10 degrees
    control_input = 1
    send(message)
    message ='land'
    send(message)
    
    # Handle ctrl-c case to quit and close the socket
  except KeyboardInterrupt as e:
    message='emergency' # try to turn off motors
    send(message)
    CmdSock.close()
    StateSock.close()  # socket for state
    stateStop.set()  # set stop variable
    writeDataFile(State_data_file_name)
    stateThread.join()   # wait for termination of state thread
    print("sockets and threads closed")
    break