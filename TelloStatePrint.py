# read tello state and put it in nice form, such as csv file.
# b'mid:64; x:0; y:0; z:0 ;mpry:0,0,0; pitch:-3; roll:-7; yaw:87; vgx:0;vgy:0;vgz:0;
 # 0          1    2    3      4         5          6         7     8     9      10
# templ:80;temph:82;tof:10; h:0; bat:80; baro:218.46; 
 # 11       12      13      14    15      16
# time:13; agx:-67.00; agy:125.00; agz:-992.00;\r\n'
#   17      18          19           20


import socket
from time import sleep
import time
import numpy as np
from queue import Queue

State_data_file_name = 'statedata.txt'
INTERVAL = 0.1
index = 0 # index for state packet
start_time = time.time()

dataQ = Queue()

def writeFileHeader(dataFileName):
    fileout = open(dataFileName,'w')
    #write out parameters in format which can be imported to Excel
    today = time.localtime()
    date = str(today.tm_year)+'/'+str(today.tm_mon)+'/'+str(today.tm_mday)+'  '
    date = date + str(today.tm_hour) +':' + str(today.tm_min)+':'+str(today.tm_sec)
    fileout.write('"Data file recorded ' + date + '"\n')
# header information
    fileout.write('index,    time,   mid,x ,y, z, mp, mr, my, pitch, roll, \
                  yaw, vgx, vgy, vgz, templ, temph, tof, h,bat,baro,time,agx,agy,agz\n\r')
    fileout.close()

def writeDataFile(dataFileName):
    fileout = open(State_data_file_name, 'a')  # append
    print('writing data to file')
    while not dataQ.empty():
        telemdata = dataQ.get()
        np.savetxt(fileout , [telemdata], fmt='%7.3f', delimiter = ',')  # need to make telemdata a list
    fileout.close()

def report(str):
#    stdscr.addstr(0, 0, str)
#    stdscr.refresh()
    begin_time=time.time()
    telemdata=[]
    telemdata.append(index)
    telemdata.append(time.time()-start_time)
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
    end_time = time.time()
#    print('Report function took %7.3f msec' % (1000*(end_time-begin_time)))
    if (index %50) == 0:
        print(index, end=',')
 
 
    
    
if __name__ == "__main__":
 #   stdscr = curses.initscr()
 #   curses.noecho()
 #   curses.cbreak()

    local_ip = ''
    local_port = 8890
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    tello_ip = '192.168.10.1'
    tello_port = 8889
    tello_adderss = (tello_ip, tello_port)

    socket.sendto('command'.encode('utf-8'), tello_adderss)
    writeFileHeader(State_data_file_name)
    try:
        index = 0
        while True:
            index += 1
            response, ip = socket.recvfrom(1024)
            if response == b'ok':
                continue
 # .replace formatting gives error in python 3?
 #           out = response.replace(';', ';\n')
            out = 'Tello State:\n' + str(response)
#            print(out)
            report(str(response))
            sleep(INTERVAL)
    except KeyboardInterrupt:
 #       curses.echo()
 #       curses.nocbreak()
 #       curses.endwin()
        print('Closed by keyboard interrupt')
        socket.close()
        writeDataFile(State_data_file_name)

