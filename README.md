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
seems to not be working in Spyder on Ubuntu.

