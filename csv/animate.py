###
# Author: Randall P (rbpittman)
# Takes link data as csv for 4X V100, animates links
# TODO: Better desc
###
from __future__ import print_function

import turtle
import csv
import time
from collections import Counter


#    0          1           2         3          4           5         6          7
#GPU0_L0_rx,GPU0_L0_tx,GPU0_L1_rx,GPU0_L1_tx,GPU0_L2_rx,GPU0_L2_tx,GPU0_L3_rx,GPU0_L3_tx,
#   8            9           10       11          12         13       14          15
#GPU1_L0_rx,GPU1_L0_tx,GPU1_L1_rx,GPU1_L1_tx,GPU1_L2_rx,GPU1_L2_tx,GPU1_L3_rx,GPU1_L3_tx,
#     16         17          18        19         20         21        22         23          24       25
#GPU2_L0_rx,GPU2_L0_tx,GPU2_L1_rx,GPU2_L1_tx,GPU2_L2_rx,GPU2_L2_tx,GPU2_L3_rx,GPU2_L3_tx,GPU2_L4_rx,GPU2_L4_tx,
#     26         27         28         29         30         31        32         33         34         35
#GPU3_L0_rx,GPU3_L0_tx,GPU3_L1_rx,GPU3_L1_tx,GPU3_L2_rx,GPU3_L2_tx,GPU3_L3_rx,GPU3_L3_tx,GPU3_L4_rx,GPU3_L4_tx

"""
ID: index/column of dataset 
GPU: GPU id
Link: Link id for specific GPU
Type: transmit (tx) or receive (rx)
Conn: Connection ID for this link

ID GPU Link Type Conn
0  0 0 rx 31
1  0 0 tx 30
2  0 1 rx 19
3  0 1 tx 18
4  0 2 rx 9
5  0 2 tx 8
6  0 3 rx 35
7  0 3 tx 34
8  1 0 rx 5
9  1 0 tx 4
10 1 1 rx 29
11 1 1 tx 28
12 1 2 rx 17
13 1 2 tx 16
14 1 3 rx 23
15 1 3 tx 22
16 2 0 rx 13
17 2 0 tx 12
18 2 1 rx 3
19 2 1 tx 2
20 2 2 rx 27
21 2 2 tx 26
22 2 3 rx 15
23 2 3 tx 14
24 2 4 rx 33
25 2 4 tx 32
26 3 0 rx 21
27 3 0 tx 20
28 3 1 rx 11
29 3 1 tx 10
30 3 2 rx 1
31 3 2 tx 0
32 3 3 rx 25
33 3 3 tx 24
34 3 4 rx 7
35 3 4 tx 6
"""

#delay in seconds
DELAY = 1
#size factor
FACTOR = 150
SQUARE_SIZE = 0.3
HSL = SQUARE_SIZE/2 #Half side length
# HDL = HSL*2**0.5 #Half diagonal length

links = []

def on_click(x,y):
    links.append((x/float(FACTOR), y/float(FACTOR)))
    print("X")
    if len(links) == 18:
        print(links)

class V100X4:
    #NOTE: Uses a scaled measurement system where gpus are at unit
    #coordinates. Scaling is done automatically with wrapper
    #functions.
    
    links = None #9 links, rx and tx, probably duplicated. 4X9=36 length list
    # link_locs = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    square_pos = [(1, 1), (1, -1), (-1, -1),  (-1, 1)]#GPU 0,1,2,3
    
    """
    link_starts_ends = [[(square_pos[0][0] - ARROW_SPACE - HSL, square_pos[0][1] + SQUARE_SIZE/6), #00
                         (square_pos[3][0] + ARROW_SPACE + HSL, square_pos[3][1] + SQUARE_SIZE/6)],
                        [(square_pos[0][0] - ARROW_SPACE - HSL, square_pos[0][1] - ARROW_SPACE - HSL), #01
                         (square_pos[2][0] + ARROW_SPACE + HSL, square_pos[2][1] + ARROW_SPACE + HSL)],
                        [(square_pos[0][0]                    , square_pos[0][1] - ARROW_SPACE - HSL), #02
                         (square_pos[1][0]                    , square_pos[1][1] + ARROW_SPACE + HSL)],
                        [(square_pos[0][0] - ARROW_SPACE - HSL, square_pos[0][1] - SQUARE_SIZE/6), #03
                         (square_pos[3][0] + ARROW_SPACE + HSL, square_pos[3][1] - SQUARE_SIZE/6)],
                        [(square_pos[1][0]                    , square_pos[1][1] + ARROW_SPACE + HSL), #10
                         (square_pos[0][0]                    , square_pos[0][1] - ARROW_SPACE - HSL)],
    """
    
    def __init__(self, data):
        self.data = data
        self.t = turtle.Turtle()
        self.t.ht()
        self.t.pu()
        self.t.tracer(0, 0)
        turtle.ht()
        self.t.speed(0)
        turtle.onscreenclick(on_click)
        
    def _square(self, x, y):
        # x *= FACTOR
        # y *= FACTOR
        self.goto(x - HSL, y - HSL)
        self.pd()
        self.goto(x - HSL, y + HSL)
        self.goto(x + HSL, y + HSL)
        self.goto(x + HSL, y - HSL)
        self.goto(x - HSL, y - HSL)
        self.pu()

    def goto(self, x, y):
        x *= FACTOR
        y *= FACTOR
        self.t.goto(x, y)
        
    def pd(self):
        self.t.pd()
    def pu(self):
        self.t.pu()

    #Post: Returns two tuples of coordinates for an arrow for link i
    def _get_start_end(self, i):
        pass

    def _draw_link(self, i):
        pass
    
    def draw(self, row):
        turtle.clearscreen()
        # self._square(-1, -1)
        # self._square( 1, -1)
        # self._square( 1,  1)
        # self._square(-1,  1)
        for pos in V100X4.square_pos:
            print("X")
            self._square(*pos)
            self._square(*pos)
        # while len(links) != 18:
        #     time.sleep(1)
        # for i in range(1, 36, 2):
        #only tx
        # self._draw_link(i)
        # print(links)
        turtle.update()
    
    def animate(self):
        # for row in self.data:
        self.draw([])
        # time.sleep(DELAY)
        print("main")
        turtle.mainloop()
        

if __name__ == "__main__":
    reader = csv.reader(open("nvlink_usage_H1.csv", 'r'))

    next(reader)
    data = [[float(x) for x in line] for line in reader]

    slope_data = []
    print("WARNING: Assuming Kbytes is y unit!!!")
    for i in range(1, len(data)):
        entry1 = data[i-1]
        entry2 = data[i  ]
        elapsed_time = entry2[0] - entry1[0]
        new_line = []
        for column in range(2, 38):
            delta_col = (entry2[column] - entry1[column]) / elapsed_time
            # new_line.append((delta_col * 8000) / (10 ** 9))
            new_line.append(delta_col)
        slope_data.append(new_line)
    v100s = V100X4(slope_data)
    v100s.animate()
