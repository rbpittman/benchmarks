import os, time, sys, log_util

NET_LOGGER_LOG_FILE = "net_logger.log"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Expected delay interval (float)")
    if len(sys.argv) < 3:
        raise Exception("Expected data output filename")
    delay = float(sys.argv[1])
    out_file = sys.argv[2]
    net_logger = log_util.NetLogger(delay, out_file, NET_LOGGER_LOG_FILE)
    net_logger.start()
    
