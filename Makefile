nvlink_logger: nvlink_logger.o
	nvcc $^ -o $@ -lnvidia-ml

nvlink_logger.o: nvlink_logger.cu
	nvcc -c nvlink_logger.cu


clean:
	rm nvlink_logger.o nvlink_logger > /dev/null 2>&1
