from __future__ import print_function
import sys, csv, pickle

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print("Expected filename and min and max times")
        sys.exit()
    if len(sys.argv) >= 5:
        print("Too many args")
        sys.exit()
    _, filename, min_time, max_time = sys.argv
    min_time = float(min_time)
    max_time = float(max_time)
    reader = csv.reader(open(filename, 'r'))
    reader.next()
    found_min = False
    found_max = False
    
    min_row = None
    max_row = None
    lines = [line for line in reader]
    for i, row in enumerate(lines):
        t = float(lines[i][0])
        if min_time <= t and not found_min:
            found_min = True
            min_row = lines[i]
        if max_time <= t and not found_max:
            found_max = True
            max_row = lines[i-1]
            break
    else:
        print("Exceeded bounds")
        sys.exit()
    gpu_link_ids = pickle.load(open('gpu_link_ids_8XV100.pkl', 'r'))
    link_dict    = pickle.load(open('link_dict_8XV100.pkl', 'r'))
    
    if found_min and found_max:
        min_row = [float(x) for x in min_row]
        max_row = [float(x) for x in max_row]
        elapsed_time = max_row[0] - min_row[0]
        requested_elapsed = max_time - min_time
        print("Elapsed time: %f (you requested %f)" %(elapsed_time, requested_elapsed))
        if abs(elapsed_time - requested_elapsed) >= 1:
            print("WARNING: elapsed time for detected entries was %f, but the delta time you requested was %f" % (elapsed_time, max_time - min_time))
        output_data = []
        for i in range(len(min_row)-1):
            GBps = (max_row[i+1] - min_row[i+1]) / (elapsed_time * 8 * 2 ** 30)
            src, link_id = gpu_link_ids[i]
            dest = link_dict[(src, link_id)]
            output_data.append([src, dest, GBps])
        output_data.sort()
        GBpss = [row[2] for row in output_data]
        avg = sum(GBpss)/len(GBpss)
        for src, dest, GBps in output_data:
            print("GPU %d to GPU %d averaged %s GBps" % (src, dest, ("%.3f" % GBps).rstrip("0").rstrip('.')))
        print("Total avg:", avg)
