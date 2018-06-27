import os, sys, time, log_util

constant_num_gpus = None
constant_num_links_per_gpu = None #List

LOG_FILENAME = "nvlink_logger.log"
# log_file_handle = open(LOG_FILENAME, 'a')
# def log(msg):
#     log_file_handle.write("[%f] "%time.time() + msg + "\n")

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

def get_link_util(logger):
    global constant_num_gpus, constant_num_links_per_gpu
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
            link_str = line_data[1][:-1]
            
            if not link_str.isdigit():
                logger.log("Invalid data")
                return -1, -1
            if link_index != int(link_str):
                logger.log("Out of order or missing link index")
            rx_data.append(int(line_data[ 3]) * 8000)
            tx_data.append(int(line_data[-2]) * 8000)
            # total_rx_kb += int(line_data[3])
            # total_tx_kb += int(line_data[-2])
            # count += 1
    if gpu_index == -1:
        logger.log("Error: no GPUs found")
        return -1, -1
    num_links_per_gpu.append(link_index+1)
    num_gpus = gpu_index + 1

    #Check consistent nvidia-smi nvlink output
    if constant_num_gpus == None:
        constant_num_gpus = num_gpus
        constant_num_links_per_gpu = num_links_per_gpu
    else:
        if num_gpus != constant_num_gpus:
            logger.log("Error: invalid number of GPUs provided by nvidia-smi nvlink")
            return -1, -1
        if num_gpus != len(num_links_per_gpu):
            raise Exception("Program bug")
        for i in range(num_gpus):
            if num_links_per_gpu[i] != constant_num_links_per_gpu[i]:
                logger.log("Error: nvidia-smi nvlink returned an inconsistant number of links for GPU index %d" % i)
                return -1, -1

    #Interleave rx_data and tx_data
    all_data = [rx_data[i//2] if i % 2 == 0 else tx_data[i//2] for i in range(2 * len(rx_data))]
    # avg_rx_kb = total_rx_kb / float(count)
    # avg_tx_kb = total_tx_kb / float(count)
    # avg_rx_mb = avg_rx_kb / 1024
    # avg_tx_mb = avg_tx_kb / 1024
    return all_data

if __name__ == "__main__":
    os.system("nvidia-smi nvlink -sc 0bz > /dev/null")
    
    if len(sys.argv) <= 1:
        delay = 1
    else:
        delay = float(sys.argv[1])
        
    if len(sys.argv) > 2:
        output_file = sys.argv[2] #overwrites global
    logger = log_util.Log(LOG_FILENAME)
    logger.log("Started new run")
    init_output()
    
    start_time = None
    kill_process = log_util.KillProcess()
    while not kill_process.kill_now:
        data_row = get_link_util(logger)
        curr_time = time.time()
        if start_time == None:
            logger.log("init start time")
            start_time = curr_time
            elapsed = 0
            # Construct csv file header
            header = "Time(sec)"
            gpu_idx = 0
            header += ",sum"
            for gpu_links in constant_num_links_per_gpu:
                for link_i in range(gpu_links):
                    header += ",GPU%d_L%d_rx" % (gpu_idx, link_i)
                    header += ",GPU%d_L%d_tx" % (gpu_idx, link_i)
                gpu_idx += 1
            send_output(header)
        else:
            elapsed = curr_time - start_time
        # send_output("%f,%f,%f" % (elapsed, rx_mb, tx_mb))
        send_output(("%f,%f" + (",%f") * len(data_row)) % (elapsed, sum(data_row), *data_row))
        time.sleep(delay)
    logger.log("Kill signal received, shutting down...")
    output_file_handle.close()
    logger.log("Shutdown complete")
