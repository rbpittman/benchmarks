from __future__ import print_function
from matplotlib import pyplot as plt
import re, math

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

NUM_LINKS = [[0, 1, 1, 2, 2, 0, 0, 0],
             [1, 0, 2, 1, 0, 2, 0, 0],
             [1, 2, 0, 2, 0, 0, 1, 0],
             [2, 1, 2, 0, 0, 0, 0, 1],
             [2, 0, 0, 0, 0, 1, 1, 2],
             [0, 2, 0, 0, 1, 0, 2, 1],
             [0, 0, 1, 0, 1, 2, 0, 2],
             [0, 0, 0, 1, 2, 1, 2, 0]]


#Data size for which ms scaling should be used instead of us. 
MS_DATA_SIZE = 100 * 2**20
SHOW_HIST = False

LAT_TEST_SIZES = [4, 102400, 1048576, 104857600]
LAT_TEST_SIZE_LABELS = ["4 bytes", "100KB", "1MB", "100MB"]

BW_TEST_SIZES = [5] + [10 ** i for i in range(1, 9)]

class Entry:
    #if is_dma, then dma is active.
    #otherwise, p2p is active. 
    def __init__(self, src_gpu, dest_gpu, MBps, lat_ms, data_size, is_dma):
        self.src_gpu = src_gpu
        self.dest_gpu = dest_gpu
        self.MBps = MBps
        self.lat_ms = lat_ms
        self.data_size = data_size
        self.is_dma = is_dma

    def __str__(self):
        return "GPU %d -> %d: bw=%f, lat_ms=%f, data_size=%d, dma=%s" % (self.src_gpu, self.dest_gpu, self.MBps, self.lat_ms, self.data_size, str(self.is_dma))

    def is_one_hop(self):
        global trans_matrix
        return trans_matrix[self.src_gpu][self.dest_gpu] == 1

    def num_links(self):
        global NUM_LINKS
        return NUM_LINKS[self.src_gpu][self.dest_gpu]

    #Returns a tuple identifying the conditions for the test that
    #the entry represents. 
    def get_conditions(self):
        # return (self.src_gpu, self.dest_gpu, self.data_size, self.is_dma)
        return self.data_size

    def is_bw_size_test(self):
        global BW_TEST_SIZES
        return self.data_size in BW_TEST_SIZES

    def is_lat_size_test(self):
        global LAT_TEST_SIZES
        return self.data_size in LAT_TEST_SIZES

# def is_one_hop(start_gpu, end_gpu):
#     global trans_matrix
#     return trans_matrix[start_gpu][end_gpu] == 1

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


lines = f.readlines()
line_i = 0

#Contains a bunch of Entry objects
all_data = []

#Known that there are 3 sets of data
for _ in range(3):
    line = lines[line_i]
    #Cycle to ======
    while "======" not in line:
        line_i += 1
        line = lines[line_i]
    
    #next is "Size:" line 
    line_i += 1
    line = lines[line_i]
    assert "Size:" in line
    data_size = int(line.split(' ')[1])
    #Skip to type of test
    line_i += 2
    line = lines[line_i]
    is_dma = "DMA" in line

    pattern = re.compile(r"Copying from GPU ([0-9]) to GPU ([0-9]): ([0-9]+\.[0-9]+) MB/s \(([0-9]+\.[0-9]+) ms\)")
    while "======" not in line:
        if "Size:" in line:
            data_size = int(line.split(' ')[1])
        else:
            match = re.match(pattern, line.strip())
            if match != None:
                groups = match.groups()

                src  = int(groups[0])
                dest = int(groups[1])
                MBps = float(groups[2])
                lat_ms = float(groups[3])
                all_data.append(Entry(src, dest, MBps, lat_ms, data_size, is_dma))
        line_i += 1
        line = lines[line_i]

#Finds entries with identical condition variables (src_gpu, dest_gpu,
#data_size, is_dma) and averages them.
#Returns a list of new entries. These entries have their lat_ms and MBps
#parameters averaged. 
def average_dup_entries(entries, reduction_factor):
    entries_dict = {}
    for entry in entries:
        conditions = entry.get_conditions()
        if conditions not in entries_dict:
            entries_dict[conditions] = [[], []]
        entries_dict[conditions][0].append(entry.MBps)
        entries_dict[conditions][1].append(entry.lat_ms)
    unique_entries = []
    for conditions, MBpss_and_lat_mss in entries_dict.items():
        MBpss, lat_mss = MBpss_and_lat_mss
        data_size = conditions
        new_entry = Entry(None, None,
                          mean(MBpss)/float(reduction_factor),
                          mean(lat_mss)/float(reduction_factor), data_size, None)
        unique_entries.append(new_entry)
    unique_entries.sort(key=lambda e: e.data_size)
    return unique_entries

def get_bw(entries):
    return [entry.MBps for entry in entries]

def get_lat(entries):
    return [entry.lat_ms for entry in entries]

def shift(x, value):
    return [a + value for a in x]

def plot_8(fig_id):
    fig_id = fig_id.lower()
    if fig_id not in ["a", "b"]:
        raise Exception("Unexpected parameter \"%s\"" % fig_id)
    is_dma = fig_id == "b"
    
    global all_data
    all_my_data = [entry for entry in all_data if entry.is_bw_size_test() and entry.is_dma == is_dma]
    
    #Grab all the entries for a given type, including duplicates
    all_one_hop = [entry for entry in all_my_data if entry.is_one_hop()]
    all_one_hop_1link = [entry for entry in all_one_hop if entry.num_links() == 1]
    all_one_hop_2link = [entry for entry in all_one_hop if entry.num_links() == 2]
    

    #Remove duplicates
    one_hop_1link = average_dup_entries(all_one_hop_1link, 2**10)
    one_hop_2link = average_dup_entries(all_one_hop_2link, 2**10)
    
    x  = BW_TEST_SIZES
    y_1hop_1link = get_bw(one_hop_1link)
    y_1hop_2link = get_bw(one_hop_2link)
    
    plt.plot(x, y_1hop_1link, 's' , color='orange', linestyle='--', linewidth=3, markersize=10, label="Inter GPU 1-hop (1 nvlink)")
    plt.plot(x, y_1hop_2link, 'd' , color='orange', linestyle='--', linewidth=3, markersize=10, label="Inter GPU 1-hop (2 nvlinks)")
    
    if not is_dma:
        all_two_hop = [entry for entry in all_my_data if not entry.is_one_hop()]
        two_hop = average_dup_entries(all_two_hop, 2**10)
        y_2hop  = get_bw(two_hop)
        plt.plot(x, y_2hop, 'bo', color='b', linestyle='--', linewidth=3, markersize=10, label="Inter GPU 2-hop")
    
    plt.legend(loc="upper left")
    plt.xscale("log")
    plt.xlabel("Data size (bytes)")
    plt.ylabel("GiBps")
    plt.title("GPU-to-GPU memory copy (No DMA)")
    # plt.title("GPU-to-GPU DMA")
    plt.show()

#index is in range [0-3]. Corresponds to each of the test sizes the paper has. 
def plot_9(index):
    my_data_size = LAT_TEST_SIZES[index]
    increase_factor = 1 if my_data_size == 100 * 2 ** 20 else 1000
    
    global all_data
    all_my_data = [entry for entry in all_data if entry.is_lat_size_test() and entry.data_size == my_data_size and entry.src_gpu == 0]
    x = [entry.dest_gpu for entry in all_my_data]
    y = [entry.lat_ms * increase_factor for entry in all_my_data]

    ax = plt.subplot(111)
    ax.bar(x, y, color="orange", tick_label=["0-%d" % i for i in range(1, len(y)+1)], label="p2p memcpy", align='center')
    plt.xlabel("src-dest")
    plt.ylabel("Latency, ms" if increase_factor == 1 else "Latency, us")
    plt.title("Latency for p2p memcpy, data size: %s" % LAT_TEST_SIZE_LABELS[index])
    plt.show()


def plot_dma_lat_comp(data_size):
    increase_factor = 1000
    global all_data
    all_my_data = [entry for entry in all_data if entry.is_bw_size_test() and entry.data_size == data_size and entry.src_gpu == 0]
    dma = [entry for entry in all_my_data if entry.is_dma]
    p2p = [entry for entry in all_my_data if not entry.is_dma]
    
    x = [entry.dest_gpu for entry in p2p]
    y_p2p = [entry.lat_ms * 1000 for entry in p2p]
    y_dma = [entry.lat_ms * 1000 for entry in dma]
    #pad 0s for unsupported x values
    y_dma += [0] * (len(x)-len(y_dma))
    ax = plt.subplot(111)
    tick_label = ["0-%d" % i for i in range(1, len(x)+1)]
    
    width = 0.4
    space = 0.05
    ax.bar(x                    , y_p2p, width, color="orange", tick_label=tick_label, label="p2p memcpy")
    ax.bar(shift(x, width+space), y_dma, width, color="blue"  , tick_label=tick_label, label="DMA")
    ax.set_xticks(shift(x, width+space/2))
    plt.xlim(1-2*space, 8+space)
    plt.legend(loc="upper left")
    plt.xlabel("src-dest")
    plt.ylabel("Latency, ms" if increase_factor == 1 else "Latency, us")
    data_size_exp = int(round(math.log(data_size, 10)))
    data_size_str = "5 bytes" if data_size == 5 else "10^%d bytes" % data_size_exp
    plt.title("Latency for p2p memcpy, data size: %s" % data_size_str)
    plt.show()

# plot_8("a")
# plot_8("b")

#for i in range(4): plot_9(i)

#for data_size in BW_TEST_SIZES:
#    plot_dma_lat_comp(data_size)




"""
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
            #Log the data
            entry = [size_in_bytes, mean(data[0])]
            if not is_dma:
                entry.append(mean(data[1]))
            results.append(entry)
            
            if SHOW_HIST:
                data[0].sort()
                plt.hist(data[0], 20, label="1-hop")
                if not is_dma:
                    data[1].sort()
                    plt.hist(data[1], 20, label='2-hop')
                plt.title("Histogram of Bandwidths between various links (Data size - %d bytes)" % size_in_bytes)
                plt.xlabel("Bandwidth (GBps)")
                plt.ylabel("Occurences")
                plt.legend()
                plt.show()

            #Reset
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
# fig8a = parse_lat(False)
# fig8b = parse_bw(True)
# fig9  = parse_lat()
"""

#parse_lat returns list of [data_size, data] where data_size is the
#size of the data being transferred, and data is a 2D list with
#entries of the form [gpu_dest, latency]
"""
p2p_memcpy_data = parse_lat()
dma_data = parse_lat()
assert(len(p2p_memcpy_data) == len(dma_data))
for i in range(len(p2p_memcpy_data)):
    data_size0, data0 = p2p_memcpy_data[i]
    data_size1, data1 = dma_data[i]
    assert data_size0 == data_size1
    
    x = get_col(data0, 0)
    x_left = [t-0.5 for t in x]
    x_right = [t for t in x]
    
    y1 = get_col(data0, 1)
    y2 = get_col(data1, 1)
    y2 += [0,0,0]#3 GPUs don't support DMA
    print(y1)
    print(y2)
    ax = plt.subplot(111)
    ax.bar(x_left , y1, width=0.35, color="orange", tick_label=["0-%d" % i for i in range(1, len(y1)+1)], label="peer-to-peer")
    ax.bar(x_right, y2, width=0.35, color="b"     , tick_label=["0-%d" % i for i in range(1, len(y1)+1)], label="DMA")
    # ax.autoscale(tight=True)
    plt.title("Latency of GPU-to-GPU mem copy - data size %d" % data_size0)
    plt.xlabel('Latency from GPU 0 to GPU n')
    # if data_size == MS_DATA_SIZE:
    #     plt.ylabel('Latency, ms')
    # else:
    #     plt.ylabel('Latency, us')
    plt.show()

"""
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
