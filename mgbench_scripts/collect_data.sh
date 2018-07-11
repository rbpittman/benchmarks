#!/bin/bash
cd ~/mgbench

# BW_SIZES="5 10 100 1000 10000 100000 1000000 10000000 100000000";
# LATENCY_SIZES="4 102400 1048576 104857600"; #4byte, 100KB, 1MB, 100MB

# run_exec() {
#     for size in $2; do
# 	echo "Size: $size bytes";
# 	echo "------------------------";
# 	$1 -size $size;
# 	echo "";
#     done
# }

# echo "Figure 8a";
# echo "=========";
# run_exec ./build/halfduplex "$BW_SIZES"

# echo "Figure 8b";
# echo "=========";
# run_exec ./build/uva "$BW_SIZES"

# echo "Figure 9";
# echo "=========";
# run_exec ./build/halfduplex "$LATENCY_SIZES"

/home/ubuntu/benchmarks/nvlink_logger 0 &

./build/halfduplex -size 10737418240 -repetitions 1

kill `jobs -rp`;

exit 0;
