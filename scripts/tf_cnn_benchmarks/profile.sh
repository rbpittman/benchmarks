#!/bin/bash

#nvprof --unified-memory-profiling off --metrics sm_efficiency python3 tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --variable_update=parameter_server

echo "Resetting nvlink counters"
nvidia-smi nvlink -sc 0bz > /dev/null;
echo "Starting background logger"

# logger() {
#     while true; do
# 	nvidia-smi nvlink -g 0;
# 	sleep 1;
#     done
# }

python3 nvlink_logger.py > test.txt &

VARIABLE_UPDATE=replicated
#nvprof --unified-memory-profiling off --metrics nvlink_transmit_throughput \
python3 tf_cnn_benchmarks.py --data_format=NCHW --batch_size=256 \
       --model=resnet50 --optimizer=momentum --variable_update=$VARIABLE_UPDATE \
       --gradient_repacking=4 --num_gpus=4 \
       --num_batches=50 --weight_decay=1e-4 --use_fp16 \
       --display_every=10

#Kill logger
kill $(jobs -rp)

#--local_parameter_device=cpu \
#       --trace_file=traces/var_update_${VARIABLE_UPDATE}_cpu_K80.json \
#       --train_dir=./train_dir
