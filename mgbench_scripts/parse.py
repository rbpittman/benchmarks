from __future__ import print_function
from matplotlib import pyplot as plt
import re

f = open("results.txt", 'r')
line = f.readline()

trans_matrix = [[0, 1, 1, 1, 1, 2, 2, 2],
                [1, 0, 1, 1, 2, 1, 2, 2],
                [1, 1, 0, 1, 2, 2, 1, 2],
                [1, 1, 1, 0, 2, 2, 2, 1],
                [1, 2, 2, 2, 0, 1, 1, 1],
                [2, 1, 2, 2, 1, 0, 1, 1],
                [2, 2, 1, 2, 1, 1, 0, 1],
                [2, 2, 2, 1, 1, 1, 1, 0]]

#Data size for which ms scaling should be used instead of us. 
MS_DATA_SIZE = 100 * 2**20

def is_one_hop(start_gpu, end_gpu):
    global trans_matrix
    return trans_matrix[start_gpu][end_gpu] == 1

def cycle_to(s):
    global f, line
    while s not in line:
        line = f.readline()
        
def mean(l):
    if len(l) == 0: raise Exception("Cannot take mean of empty list")
    return sum(l)/float(len(l))

def csv_print(data):
    for row in data:
        print(",".join([str(x) for x in row]))

def get_col(matrix, col):
    if len(matrix) == 0:
        raise Exception("Empty matrix")
    if len(matrix[0]) == 0:
        raise Exception("No columns")
    if col >= len(matrix[0]):
        raise Exception("Column %d out of range for matrix with %d columns" % (col, len(matrix[0])))
    return [row[col] for row in matrix]

def parse_bw(is_dma):
    global f, line
    cycle_to("======")
    line = f.readline()
    size_in_bytes = int(line.split(' ')[1])
    pattern = re.compile(r"Copying from GPU ([0-9]) to GPU ([0-9]): ([0-9]+\.[0-9]+).*")
    line = f.readline()
    data = [[], []]
    results = []
    while "======" not in line:
        #Grab size section
        if "Size:" in line or "Figure" in line:
            entry = [size_in_bytes, mean(data[0])]
            if not is_dma:
                entry.append(mean(data[1]))
            results.append(entry)
            """
            data[0].sort()
            data[1].sort()
            print(size_in_bytes, data)
            plt.hist(data[0])
            plt.hist(data[1])
            plt.show()
            """
            data = [[], []]
            if "Size:" in line:
                size_in_bytes = int(line.split(' ')[1])
        else:
            match = re.match(pattern, line)
            if match:
                start_gpu = int  (match.groups()[0])
                end_gpu   = int  (match.groups()[1])
                MBps      = float(match.groups()[2])
                GBps = MBps/1024.
                if is_one_hop(start_gpu, end_gpu):
                    data[0].append(GBps)
                else:
                    data[1].append(GBps)
        
        line = f.readline()
    return results


def parse_lat():
    global f, line
    cycle_to("======")
    line = f.readline()
    size_in_bytes = int(line.split(' ')[1])
    pattern = re.compile(r"Copying from GPU ([0-9]) to GPU ([0-9]): [0-9]+\.[0-9]+ MB/s \(([0-9]+\.[0-9]+)\sms\)")
    line = f.readline()
    data = []
    results = []
    while "======" not in line:
        #Grab size section
        if "Size:" in line or "Figure" in line:
            results.append([size_in_bytes, data])
            data = []
            if "Size:" in line:
                size_in_bytes = int(line.split(' ')[1])
        else:
            match = re.match(pattern, line)
            if match:
                start_gpu = int  (match.groups()[0])
                end_gpu   = int  (match.groups()[1])
                latency   = float(match.groups()[2])
                if size_in_bytes != MS_DATA_SIZE:
                    latency = latency* (10**3)
                if start_gpu == 0:
                    data.append([end_gpu, latency])
        line = f.readline()
    return results

fig8a = parse_bw(False)
fig8b = parse_bw(True)
fig9  = parse_lat()

print("8a:")
csv_print(fig8a)

print("8b:")
csv_print(fig8b)

print("9:")
print(fig9)
for plot_data in fig9:
    data_size, data = plot_data
    # print(data_size, data)
    x = get_col(data, 0)
    print(x)
    y = get_col(data, 1)
    print(y)
    plt.bar(x, y, color="orange", tick_label=["0-%d" % i for i in range(1, 8)], align='center')
    plt.title("Latency of GPU-to-GPU mem copy - data size %d" % data_size)
    plt.xlabel('Latency from GPU 0 to GPU n')
    if data_size == MS_DATA_SIZE:
        plt.ylabel('Latency, ms')
    else:
        plt.ylabel('Latency, us')
    plt.show()

"""
#Plot figure 8a (and 8b if re-commented correctly)
x  = get_col(fig8b, 0)
y1 = get_col(fig8b, 1)#1hop
# y2 = get_col(fig8a, 2)#2hop
line1 = plt.plot(x, y1, 's', color='orange', linestyle='--', linewidth=3, markersize=10, label="Inter GPU 1-hop")
#line2 = plt.plot(x, y2, 'bo', color='b', linestyle='--', linewidth=3, markersize=10, label="Inter GPU 2-hop")
plt.legend(loc="upper left")
plt.xscale("log")
plt.xlabel("Data size (bytes)")
plt.ylabel("GiBps")
#plt.title("GPU-to-GPU memory copy")
plt.title("GPU-to-GPU DMA")
plt.show()
"""



f.close()
