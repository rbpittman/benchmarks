import signal, time, re, os

class KillProcess:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_exit)
        signal.signal(signal.SIGTERM, self.signal_exit)
    
    def signal_exit(self, signum, frame):
        self.kill_now = True

class Log:
    log_file_handle = None
    def __init__(self, log_filename):
        self.log_file_handle = open(log_filename, 'a')

    def log(self, msg):
        self.log_file_handle.write("[%f] "%time.time() + msg + "\n")
    
    def __del__(self):
        self.log_file_handle.close()

class NetLogger(Log):
    data_file = None
    delay = None
    def __init__(self, delay, data_filename, log_filename):
        if data_filename == log_filename:
            raise Exception("Can't log to same files")
        Log.__init__(self, log_filename)
        self.data_file = open(data_filename, "w")
        self.delay = delay
        self.kill_process = KillProcess()
        self.start_row = None
        
        self.num_cols = 20 #1 time entry, 1 sum entry, 1 sum receive,
        #1 sum transmit, 8 receive entries, 8 transmit entries

    
    #Pre: init has been properly run
    #Post: Returns entire row of csv file, including time, as the
    #      current value of the entry minus self.start_row. 
    def get_data(self):
        #Using cat instead of opening file directly because the OS may
        #be in the middle of a write to this file during a read, but
        #cat will allow it to be read without errors, I think...
        found_interface = False
        data_row = []
        data_line = None
        lines = os.popen("cat /proc/net/dev").readlines()
        for line in lines:
            line = line.strip()
            interface_name = line.split(' ')[0] #includes semi-colon
            #for actual interface lines
            if interface_name == "face":
                #Header line, save it for start row header if necessary
                if self.start_row == None:
                    header_line = line
            elif interface_name != "lo:" and ":" in line:#Ensure it's an interface line
                if found_interface:
                    self.log("Error: Multiple interfaces found")
                    return [-1] * self.num_cols
                found_interface = True
                data_line = line
        if not found_interface:
            self.log("Error: Could not find non lo interface")
            return [-1] * self.num_cols
        if data_line == None:
            raise("Exception: Program bug")

        raw_data = [int(x) for x in re.findall(r"[0-9]+", data_line[data_line.index(":")+1:])]
        pre_subbed_row = [time.time()]
        pre_subbed_row.append(sum(raw_data))
        pre_subbed_row.append(sum(raw_data[:8]))
        pre_subbed_row.append(sum(raw_data[8:]))
        pre_subbed_row += raw_data
        if self.start_row == None:
            #Use saved header_line to name everything
            header_line = header_line[header_line.index("|")+1:]
            header_data = re.findall(r"[a-z]+", header_line)
            header = "time(sec),sum-all,sum-rcv,sum-trans"
            for i in range(16):
                header += ",%s-%s" % ("rcv" if i < 8 else "trans", header_data[i])
            self.data_file.write(header + "\n")
            
            self.start_row = list(pre_subbed_row)
        data_row = [a - b for a,b in zip(pre_subbed_row, self.start_row)]
        return data_row

    def write_data(self, data_row):
        format_str = "%.3f" + (",%d" * (self.num_cols-1))
        output_str = format_str % tuple(data_row)
        self.data_file.write(output_str + "\n")

    #Main for this class.
    def start(self):
        while not self.kill_process.kill_now:
            data_row = self.get_data()
            self.write_data(data_row)
            time.sleep(self.delay)
        
    def __del__(self):
        self.data_file.close()
