from __future__ import print_function
import matplotlib.pyplot as plt
import turtle
import csv

# reader = csv.reader(open("4XV100_nvlink_usage.csv", 'r'))
reader = csv.reader(open("nvlink_inception3_4XV100.csv", 'r'))
next(reader)
data = [[float(x) for x in line] for line in reader]

slope_data = []
print("WARNING: Assuming bits is y unit!!!")
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

SUMMED = True

if SUMMED:
    y = [sum(row) for row in slope_data]
    plot_data = [x,y]
else:
    plot_data = []
    for i in range(18):
        y = [row[i] for row in slope_data]
        plot_data += [x, y]

"""
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

"""


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
# plt.plot(x, y)
plt.title("Variables replicated and all-reduced over each GPU")
plt.plot(*plot_data)
# plt.xlim(20, 70)
# plt.xlim(12, 13.5)
plt.xlabel("Time (sec)")
if SUMMED:
    plt.ylabel("Gbps summed tx nvlink")
else:
    plt.ylabel("Gbps all 18 tx nvlinks overlayed")
plt.tight_layout()
plt.show()
