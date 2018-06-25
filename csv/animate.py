###
# Author: Randall P (rbpittman)
# Takes link data as csv for 4X V100, animates links
# TODO: Better desc
###

import turtle
import csv
import time

#delay in seconds
DELAY = 1
#size factor
FACTOR = 150
SQUARE_SIZE = 0.3

#GPU0_L0_rx,GPU0_L0_tx,GPU0_L1_rx,GPU0_L1_tx,GPU0_L2_rx,GPU0_L2_tx,GPU0_L3_rx,GPU0_L3_tx,
#GPU1_L0_rx,GPU1_L0_tx,GPU1_L1_rx,GPU1_L1_tx,GPU1_L2_rx,GPU1_L2_tx,GPU1_L3_rx,GPU1_L3_tx,
#GPU2_L0_rx,GPU2_L0_tx,GPU2_L1_rx,GPU2_L1_tx,GPU2_L2_rx,GPU2_L2_tx,GPU2_L3_rx,GPU2_L3_tx,GPU2_L4_rx,GPU2_L4_tx,
#GPU3_L0_rx,GPU3_L0_tx,GPU3_L1_rx,GPU3_L1_tx,GPU3_L2_rx,GPU3_L2_tx,GPU3_L3_rx,GPU3_L3_tx,GPU3_L4_rx,GPU3_L4_tx
class V100X4:
    links = None #9 links, rx and tx, probably duplicated. 4X9=36 length list
    link_locs = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    link_labels = [
    def __init__(self, data):
        self.data = data
        self.t = turtle.Turtle()
        self.t.ht()
        self.t.pu()
        turtle.tracer(0)
        turtle.ht()
        
    def _square(self, x, y):
        x *= FACTOR
        y *= FACTOR
        hsl = SQUARE_SIZE * FACTOR #Half side length
        self.t.goto(x - hsl, y - hsl)
        self.t.pd()
        self.t.goto(x - hsl, y + hsl)
        self.t.goto(x + hsl, y + hsl)
        self.t.goto(x + hsl, y - hsl)
        self.t.goto(x - hsl, y - hsl)
        self.t.pu()
        
    def draw(self):
        turtle.clearscreen()
        self._square(-1, -1)
        self._square( 1, -1)
        self._square( 1,  1)
        self._square(-1,  1)
        
        turtle.update()
    
    def animate(self):
        for row in self.data:
            self.links = row
            self.draw()
            time.sleep(DELAY)
            
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
            new_line.append((delta_col * 8000) / (10 ** 9))
        slope_data.append(new_line)
    v100s = V100X4(slope_data)
    v100s.animate()
