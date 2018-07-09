#!/bin/bash

# echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &


# echo "Starting nvlink logger...";
# ./nvlink_logger 0 &
# echo "Done"

for BS in 16 32 64 128; do
    echo "auto-log-parser-reset ===========================";
    echo "LocalBS: $BS";
    python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=$BS --model=resnet50 --variable_update=replicated --all_reduce_spec=nccl
done

#--all_reduce_spec=nccl

#--data_dir=/home/ubuntu/imagenet

# for id in $(jobs -rp); do
# kill $id;
# done

kill `jobs -rp`;
