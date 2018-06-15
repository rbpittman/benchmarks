import os
import time

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
    while True:
        rx_mb, tx_mb = get_link_util()
        print(time.time(), rx_mb, tx_mb)
        time.sleep(1)
