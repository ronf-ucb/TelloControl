#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 14:01:39 2020

@author: ronf
"""

##### see what speed sleep can cycle at   #############

from time import sleep
import time
import numpy as np

INTERVAL = 0.005
index = 0 # index for state packet
start_time = time.time()

if __name__ == "__main__":
 #   stdscr = curses.initscr()
 #   curses.noecho()
 #   curses.cbreak()

   try:
        index = 0
        print('begin timing ^c to stop')
        start_time = time.time()
        while True:
            index += 1
            sleep(INTERVAL)
#            if (index % 100) == 0:
#                print('  %d  %8.4f' %(index, time.time()-start_time), end=',')
            
   except KeyboardInterrupt:
 #     
        print('Closed by keyboard interrupt')
        print('\n cycles = %d, N*Interval =%7.3f, elapsed time %7.3f' % (index, index*INTERVAL, time.time()-start_time))
