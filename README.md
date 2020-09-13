# TelloControl
python code for Tello SDK

port 8889 is used for commands
port 8890 is used for reading state
if a process does not exit cleanly, a socket may be left open.
In linux, use 
sudo netstat -a -p -e -o | grep udp
to see if port 8889 or 8890 are left open
- p show PID
-a show all
-e extended info

also this could work
sudo fuser -v 8889/udp

restarting python kernel seemed to close open sockets

maybe need to restart Tello as well if not connecting?
seems to not be working in Spyder on Ubuntu- need python kernel restart

Timing: tight loop with sleep(0.01sec) took sec for   loops, 
ideal 58.70 sec, actual 61.214 sec ==> 10.43 msec

sleep(0.005) sec, ideal 30.255, actual 32.120 ==> 05.31 msec

file write operation takes ~2 ms each. Need to bring out of loop.
queue uses < 0.2 ms per sample
state update only works at 10 Hz.

