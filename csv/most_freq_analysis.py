###
# Author: Randall P (rbpittman)
# Produces a frequency list that is helpful in figuring out which
# links are connected. Used this to figure out all link IDs. 
###
from __future__ import print_function

import turtle, re, pickle
import csv
import time
from collections import Counter

#delay in seconds
DELAY = 1
#size factor
FACTOR = 150
SQUARE_SIZE = 0.3

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

#It appears there is dual transmission involved. If there are two
#links going to the same location, both are used in parallel with an
#even split. For example, link indices 0 and 6 are each other's most
#frequent, followed by the pair they communicate with. 

class V100X4:
    links = None #9 links, rx and tx, duplicated. 4X9=36 length list
    # link_locs = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    # link_labels = []#TODO
    def __init__(self, data, gpu_link_ids):
        self.data = data
        self.gpu_link_ids = gpu_link_ids
        
    def animate(self):
        most_freq = []
        for check_col in range(len(self.data[1])):
            cols = Counter()
            for row_idx, row in enumerate(self.data):
                self.links = row
                max_dist = 100
                value = row[check_col]
                for i in range(len(row)):
                    # print(row[i], value)
                    if i != check_col and abs(row[i]-value) < max_dist:
                        cols[i] += 1
                # self.draw()
                # time.sleep(DELAY)
            common = cols.most_common(3)
            most_freq.append([e[0] for e in common])

        all_mappings = []
        for i in range(len(most_freq)):
            data = [i] + most_freq[i]
            for check_idx in range(1, len(most_freq) + 1):
                if data[check_idx] % 2 != data[0] % 2:
                    new_mapping = (data[0], data[check_idx])
                    print("%d -> %d" % new_mapping, "with confidence %d (where 1 is best, 3 is worst)" % check_idx)
                    all_mappings.append(new_mapping)
                    break
            # print(i, most_freq[i])
            # turtle.mainloop()
        success = True
        for mapping in all_mappings:
            if (mapping[1], mapping[0]) not in all_mappings:
                print("Reverse of", mapping, "not found")
                success = False
        link_matrix = []
        dic_map = {}
        if success:
            print("PASSED TEST")
            #pass each index as the index of gpu_link_ids, which will
            #then return (gpu, link), but we only want gpu.
            for mapping in all_mappings:
                start_gpu, start_link = self.gpu_link_ids[mapping[0]]
                end_gpu = self.gpu_link_ids[mapping[1]][0]
                print("%d -> link %d -> %d" % (start_gpu, start_link, end_gpu))
                dic_map[(start_gpu, start_link)] = end_gpu
        else:
            print("FAILED, not all reversals succeeded")
        pickle.dump(dic_map, open("link_dict_8XV100.pkl", 'w'))

if __name__ == "__main__":
    reader = csv.reader(open("Old/nvlink_8XV100_bs64.csv", 'r'))

    header_list = reader.next()
    pattern = re.compile(r"GPU([0-9]+)_L([0-9]+)_.x")
    gpu_link_ids = []
    for i in range(2, len(header_list)):
        match = re.match(pattern, header_list[i])
        gpu_link_ids.append([int(x) for x in match.groups()])
    #gpu_link_ids[overall_index] returns (gpu_idx, link_id)
    
    data = [[float(x) for x in line] for line in reader]

    slope_data = []
    print("WARNING: Assuming Kbytes is y unit!!!")
    print(len(data[0]))
    for i in range(1, len(data)):
        entry1 = data[i-1]
        entry2 = data[i  ]
        elapsed_time = entry2[0] - entry1[0]
        new_line = []
        for column in range(2, len(data[0])):
            delta_col = (entry2[column] - entry1[column]) / elapsed_time
            # new_line.append((delta_col * 8000) / (10 ** 9))
            new_line.append(delta_col)
        slope_data.append(new_line)
    v100s = V100X4(slope_data, gpu_link_ids)
    v100s.animate()
