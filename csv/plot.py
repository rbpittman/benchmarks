from __future__ import print_function
import matplotlib.pyplot as plt
import turtle
import csv

# reader = csv.reader(open("4XV100_nvlink_usage.csv", 'r'))
reader = csv.reader(open("nvlink_p2p_4XV100_long_run.csv", 'r'))
next(reader)
data = [[float(x) for x in line] for line in reader]

slope_data = []
print("WARNING: Assuming bytes is y unit!!!")
print("Output is in Gbps")

for i in range(1, len(data)):
    entry1 = data[i-1]
    entry2 = data[i  ]
    elapsed_time = entry2[0] - entry1[0]
    new_line = []
    for column in range(3, 38, 2):
        bps = (entry2[column] - entry1[column]) / elapsed_time
        # new_line = [entry2[0], (delta_col * 8000) / (10 ** 6)]
        new_line.append(bps / (10 ** 9))
    slope_data.append(new_line)
# x, y1 = [[row[i] for row in slope_data] for i in range(2)]
x = [row[0] for row in data[:-1]]
y = [row[4] for row in slope_data]


print("PERFORMING SPIKE SCAN OF ALL TX LINKS")

# scan_col = 5 + 2
for scan_col in range(3, 38, 2):
    start = None
    prev_link = data[0]
    spikes = []
    for i in range(1, len(data)):
        link = data[i][scan_col]
        if link != prev_link:
            if start == None:
                start = i
                prev_val = link
        else:
            if start != None:
                end = i-1
                if start == end:
                    # print("found spike of size 1, no duration")
                    pass
                else:
                    elapsed_time = data[end][0]-data[start][0]
                    GBps = (data[end][scan_col] - data[start][scan_col])/(8 * 10 ** 9 * elapsed_time)
                    if GBps > 0.001:
                        spikes.append(round(GBps, 2))
                        #print("Found spike with average rate %f with duration %f seconds." % (GBps, elapsed_time))
                    start = None
        prev_link = link
    print("Link ID [0-35]:", scan_col-2, "Spikes:", spikes, "Avg:", round(sum(spikes)/len(spikes), 2))
                
        

# print("num columns:", len(slope_data[0]))
# assert (len(slope_data[0]) == 18)
# totals = [0] * 18
# for row in slope_data:
#     for i in range(len(row)):
#         totals[i] += row[i]

    


#Analyze diff between sum rx and sum tx, turns out it hovers around
#0. Since the counters are cumulative, only the end matters, and its
#0. 
"""
for i, x_value in enumerate(x):
    row = data[i]
    rx = [row[i] for i in range(2, 38, 2)]
    tx = [row[i+1] for i in range(2, 38, 2)]
    print(sum(tx) - sum(rx))
"""

#Plot data
plt.plot(x, y)
# plt.xlim(20, 70)
# plt.xlim(12, 13.5)
plt.xlabel("Time (sec)")
plt.ylabel("Gbps summed tx nvlink communication")
plt.tight_layout()
plt.show()

# First  point at 50.95 ,  12235717 Kbytes
# second point at 129.07, 120843316 Kbytes
# Read 108607599 Kbytes in 78.12 seconds
# Averaged 11Gbps during training.

# gbps = [round(8000 * (second[i] - first[i])/(duration * 10**6), 3) for i in range(len(first))]
# GPU0_L0_rx,GPU0_L0_tx,GPU0_L1_rx,GPU0_L1_tx,GPU0_L2_rx,GPU0_L2_tx,GPU0_L3_rx,GPU0_L3_tx,GPU1_L0_rx,GPU1_L0_tx,GPU1_L1_rx,GPU1_L1_tx,GPU1_L2_rx,GPU1_L2_tx,GPU1_L3_rx,GPU1_L3_tx,GPU2_L0_rx,GPU2_L0_tx,GPU2_L1_rx,GPU2_L1_tx,GPU2_L2_rx,GPU2_L2_tx,GPU2_L3_rx,GPU2_L3_tx,GPU2_L4_rx,GPU2_L4_tx,GPU3_L0_rx,GPU3_L0_tx,GPU3_L1_rx,GPU3_L1_tx,GPU3_L2_rx,GPU3_L2_tx,GPU3_L3_rx,GPU3_L3_tx,GPU3_L4_rx,GPU3_L4_tx
# Average per link: [222.427, 277.605, 444.764, 320.368, 444.852, 533.704, 222.425, 277.599, 533.704, 444.852, 533.569, 555.149, 266.714, 160.064, 266.714, 160.062, 160.064, 266.714, 320.368, 444.764, 160.032, 277.522, 160.062, 266.714, 160.033, 277.513, 277.522, 160.032, 555.149, 533.509, 277.605, 222.413, 277.513, 160.019, 277.599, 222.412]
