#!/bin/bash

#nvprof --unified-memory-profiling off --metrics sm_efficiency python3 tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --variable_update=parameter_server

echo "Resetting nvlink counters"
nvidia-smi nvlink -sc 0bz > /dev/null;
echo "Starting background nvlink logger"
if [ ! -d nvlink_data ]; then
    mkdir nvlink_data;
fi

VARIABLE_UPDATE=parameter_server
NVLINK_FILE=nvlink_data/${VARIABLE_UPDATE}.csv
python3 nvlink_logger.py 0.5 > $NVLINK_FILE &

#nvprof --unified-memory-profiling off --metrics nvlink_transmit_throughput \
python3 tf_cnn_benchmarks.py --data_format=NCHW --batch_size=256 \
       --model=resnet50 --optimizer=momentum --variable_update=$VARIABLE_UPDATE \
       --gradient_repacking=4 --num_gpus=4 \
       --num_batches=100 --weight_decay=1e-4 --use_fp16 \
       --display_every=10

#Kill logger
kill $(jobs -rp)

#--local_parameter_device=cpu \
#       --trace_file=traces/var_update_${VARIABLE_UPDATE}_cpu_K80.json \
#       --train_dir=./train_dir
