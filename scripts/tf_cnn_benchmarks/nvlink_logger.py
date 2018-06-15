import os, sys, time, signal

class KillProcess:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_exit)
        signal.signal(signal.SIGTERM, self.signal_exit)
    def signal_exit(self, signum, frame):
        self.kill_now = True


constant_num_gpus = None
constant_num_links_per_gpu = None #List

LOG_FILE = "nvlink_logger.log"
log_file_handle = open(LOG_FILE, 'a')
def log(msg):
    log_file_handle.write("[%f] "%time.time() + msg + "\n")

output_file = "default_nvlink_output.csv"
output_file_handle = None
def init_output():
    global output_file_handle
    if output_file_handle:
        raise Exception("Program bug: output file already initialized")
    output_file_handle = open(output_file, 'w')

def send_output(msg):
    global output_file_handle
    output_file_handle.write(msg + "\n")


def get_link_util():
    # total_rx_kb = 0
    # total_tx_kb = 0
    # count = 0
    gpu_index = -1
    link_index = -1
    num_links_per_gpu = []
    rx_data = []
    tx_data = []
    for line in os.popen("nvidia-smi nvlink -g 0").readlines():
        line = line.strip()
        if "GPU" == line[:3]:
            gpu_index += 1
            if gpu_index != 0:
                #Perform link_index reset
                num_links_per_gpu.append(link_index+1)
                link_index = -1
        else:
            link_index += 1
            line_data = line.split(' ')
            #TODO: verify link_index == get_link_index(line_data)
            rx_data.append(int(line_data[ 3]))
            tx_data.append(int(line_data[-2]))
            # total_rx_kb += int(line_data[3])
            # total_tx_kb += int(line_data[-2])
            # count += 1
    if gpu_index == -1:
        log("Error: no GPUs found")
        return -1, -1
    num_links_per_gpu.append(link_index+1)
    num_gpus = gpu_index + 1

    #Check consistent nvidia-smi nvlink output
    if constant_num_gpus == None:
        constant_num_gpus = num_gpus
        constant_num_links_per_gpu = num_links_per_gpu
    else:
        if num_gpus != constant_num_gpus:
            log("Error: invalid number of GPUs provided by nvidia-smi nvlink")
            return -1, -1
        if num_gpus != len(num_links_per_gpu):
            raise Exception("Program bug")
        for i in range(len(num_gpus)):
            if num_links_per_gpu[i] != constant_num_links_per_gpu[i]:
                log("Error: nvidia-smi nvlink returned an inconsistant number of links for GPU index %d" % i)
                return -1, -1

    #Interleave rx_data and tx_data
    all_data = [rx_data[i//2] if i % 2 == 0 else tx_data[i//2] for i in range(2 * len(rx_data))]
    # avg_rx_kb = total_rx_kb / float(count)
    # avg_tx_kb = total_tx_kb / float(count)
    # avg_rx_mb = avg_rx_kb / 1024
    # avg_tx_mb = avg_tx_kb / 1024
    return all_data

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delay = 1
    else:
        delay = float(sys.argv[1])
        
    if len(sys.argv) <= 2:
        output_file = sys.argv[2] #overwrites global
    
    init_output()
    
    start_time = None
    kill_process = KillProcess()
    while not kill_process.kill_now:
        data_row = get_link_util()
        curr_time = time.time()
        if start_time == None:
            start_time = curr_time
            elapsed = 0
            # Construct csv file header
            header = "Time(sec)"
            for gpu_links in constant_num_links_per_gpu:
                for link_i in range(gpu_links):
                    header += ",GPU_%d_Link_%d_rx" % (gpu_links, link_i)
                    header += ",GPU_%d_Link_%d_tx" % (gpu_links, link_i)
                send_output(header)
        else:
            elapsed = curr_time - start_time
        # send_output("%f,%f,%f" % (elapsed, rx_mb, tx_mb))
        send_output(("%f" + (",%f") * len(all_data)) % (elapsed, *all_data))
        time.sleep(delay)
    log("Kill signal received, shutting down...")
    log_file_handle.close()
    output_file_handle.close()
    log("Shutdown complete")
