from __future__ import print_function
import matplotlib.pyplot as plt
import turtle
import csv
import sys
import argparse
import os, re, pickle

"""
This is a multi-purpose utility file, useful primarily for plotting
the data found in this csv folder. 
"""

# font = {'family' : 'normal',
#         'weight' : 'bold',
#         'size'   : 22}

font = {'size' : 20}

plt.rc('font', **font)

UNITS = ["bits", "packets", "cycles"]

USE_BYTES = True

#Whether to filter out nvlinks that don't change enugoh to be useful information
USE_MIN_FILTERING = False
MIN_CHANGES_FOR_DISPLAY = 10

scaling = {"K":10**3, "M":10**6, "G":10**9}

def get_units(filename):
    global UNITS
    
    base = filename if "/" not in filename else filename[filename.rindex("/")+1:]
    units_found = []
    for unit in UNITS:
        if unit in base:
            units_found.append(unit)

    if len(units_found) > 1:
        print("Multiple units %s provided in filename, ambiguous." % ", ".join(units_found))
        sys.exit()
    if len(units_found) < 1:
        print("No units found in filename")
        sys.exit()
    unit = units_found[0]
    return unit

gpu_link_ids = []
gpu_link_to_dest = pickle.load(open("link_dict_8XV100.pkl", 'r'))

#Takes tx index.
#Returns src gpu, dest gpu
def get_src_dest(i):
    gpu_i, link_i = gpu_link_ids[i]
    return (gpu_i, gpu_link_to_dest[(gpu_i, link_i)])

def get_link_tag(gpu_i, link_i):
    return "%d -> %d" % (gpu_i, gpu_link_to_dest[(gpu_i, link_i)])

def gpu_idx_to_tag(i):
    return get_link_tag(*gpu_link_ids[i])


def get_data(filename, summed):
    global gpu_link_ids
    unit = get_units(filename)
    if unit == "bits" and USE_BYTES:
        unit = "bytes"
        scale_fn = lambda x: x / (10 ** 9 * 8)
    else:
        scale_fn = lambda x: x / (10 ** 9)
    label = "G-" + unit + "/sec"
    reader = csv.reader(open(filename, 'r'))
    header_list = reader.next()#Skip header
    pattern = re.compile(r"GPU([0-9])+_L([0-9]+)")
    for i in range(1, len(header_list)):
        match = re.match(pattern, header_list[i])
        gpu_link_ids.append([int(x) for x in match.groups()])
    pickle.dump(gpu_link_ids, open("gpu_link_ids.pkl", 'w'))
    data = [[float(x) for x in line] for line in reader]
    slope_data = []
    column_changes = [0] * (len(data[0])-1)
    for i in range(1, len(data)):
        entry1 = data[i-1]
        entry2 = data[i  ]
        elapsed_time = entry2[0] - entry1[0]
        new_line = []
        for column in range(1, len(data[0])):
            if entry2[column] != entry1[column]:
                column_changes[column-1] += 1
            pre_scaled = (entry2[column] - entry1[column]) / elapsed_time
            scaled = scale_fn(pre_scaled)
            new_line.append(scaled)
        slope_data.append(new_line)
    src_dest_with_no_change = []
    for i, num_changes in enumerate(column_changes):
        src, dest = get_src_dest(i)
        if num_changes != 0:
            print("GPU", src,"to GPU", dest, "had", num_changes, "changes")
        else:
            src_dest_with_no_change.append((src, dest))
    print("src dest with no changes:", src_dest_with_no_change)
    # use_column = [value >= MIN_CHANGES_FOR_DISPLAY for value in column_changes]
    # print(use_column)
    x = [row[0] for row in data[:-1]]
    
    if summed:
        y = [sum(row) for row in slope_data]
        plot_data = [x,y]
    else:
        plot_data = []
        for i in range(len(slope_data[0])):
            y = [row[i] for row in slope_data]
            plot_data += [x, y]
    return plot_data, label, unit

def get_mean(data):
    return sum(data) / len(data)

def scale_data(data, factor):
    for i in range(len(data)):
        data[i] *= factor

if __name__ == "__main__":
    filenames = []
    parser = argparse.ArgumentParser(description="Plot csv graphs of nvlink utilization")
    parser.add_argument("filenames", nargs='+', help="Space separated list of csv files")
    parser.add_argument("--summed", action="store_true", help="If provided, all tx will be summed")
    args = parser.parse_args()
    if not args.summed and len(filenames) > 1:
        print("Warning: plotting multiple filenames without summed mode may break the legend")
    for filename in args.filenames:
        if not os.path.isfile(filename):
            print("Error reading file \"%s\"" % filename)
            sys.exit()
    
    all_plot_data = []
    all_labels = []
    avg_gbps = -1
    for filename in args.filenames:
        print("Parsing \"%s\"" % filename)
        plot_data, label, unit = get_data(filename, args.summed)
        all_plot_data += plot_data
        all_labels.append(label)
        if unit == "bits" and args.summed:
            avg_gbps = get_mean(plot_data[1])
    
    unit_label = all_labels[0]
    plt.ylabel(unit_label)
    if len(args.filenames) == 1 and not args.summed:
        #Then make legend include every link 
        assert len(all_labels) == 1
        all_labels = []
        assert len(gpu_link_ids) != 0
        for i in range(min([len(gpu_link_ids), 6])):
            link_tag = get_link_tag(*gpu_link_ids[i])
            all_labels.append(link_tag)
            
    if args.summed and avg_gbps != -1 and len(args.filenames) > 1:
        #Found an avg gbps, so scale remaining data by that factor
        for i, filename in enumerate(args.filenames):
            if get_units(filename) != "bits":
                y_data = all_plot_data[2 * i + 1]#[x,y,x,y,x,y...]
                factor = round((avg_gbps / get_mean(y_data)), 2)
                all_labels[i] = "%.2fX-%s" % (factor, all_labels[i])
                scale_data(y_data, factor)
    # Plot data
    plt.title("Nvlink usage")
    
    # x = all_plot_data[0]
    # delta_x = [x[i]-x[i-1] for i in range(1, len(x))]
    # plt.plot(delta_x)
    lines = plt.plot(*all_plot_data, marker='o', markersize=5)
    plt.legend(lines, all_labels, loc="best")
    
    plt.xlabel("Time (sec)")
    # plt.ylabel(", ".join(all_labels))
    # plt.ylabel("GBytes per second")
    # plt.tight_layout()
    plt.show()
    
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

#ultra_res_resnet152_v2_bs64_4XV100.csv, compute average bw during training
#93.003733,168369832,364288932,305758280,168370688,64625316,117401512,72475300,72474624,72474880,123155968,87967748,72475044,87964416,87966976,117401508,47803136,87965184,47804416
#140.002338,5327856620,13648900516,7272975992,5327909740,7000412372,12754937480,7875995132,7876017880,7851962768,13332201472,9543438764,7851974468,9543288840,9553371136,12736055508,5186709760,9553355776,5191580928

# average = 3303451093 bps = 3.3Gbps



#92 -> 139.4
#92.001950,1346954528,2914311456,2446066240,1346969632,517002528,939212096,579798304,579801088,579796992,985247744,703725568,579802400,703731744,703717376,939212064,382437376,703739904,382423040
#139.402139,43021170944,110284889376,58777786592,43021117920,56717849536,103160902016,63701737056,63701767520,63638848704,108098906112,77270652928,63638755072,77271322048,77361035264,103214453696,42016440320,77361043456,42016798720
