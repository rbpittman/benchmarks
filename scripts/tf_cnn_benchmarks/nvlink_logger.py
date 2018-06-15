import os, sys, time

def get_link_util():
    total_rx_kb = 0
    total_tx_kb = 0
    count = 0
    for line in os.popen("nvidia-smi nvlink -g 0").readlines():
        line = line.strip()
        if "GPU" != line[:3]:
            line_data = line.split(' ')
            total_rx_kb += int(line_data[3])
            total_tx_kb += int(line_data[-2])
            count += 1
    avg_rx_kb = total_rx_kb / float(count)
    avg_tx_kb = total_tx_kb / float(count)
    avg_rx_mb = avg_rx_kb / 1024
    avg_tx_mb = avg_tx_kb / 1024
    return avg_rx_mb, avg_tx_mb

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delay = 1
    else:
        delay = float(sys.argv[1])
    start_time = None
    while True:
        rx_mb, tx_mb = get_link_util()
        curr_time = time.time()
        if start_time == None:
            start_time = curr_time
            elapsed = 0
        else:
            elapsed = curr_time - start_time
        print("%f,%f,%f" % (elapsed, rx_mb, tx_mb))
        sys.stdout.flush()
        time.sleep(delay)
