#!/bin/bash

echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &
echo "Starting nvlink logger...";
python3 nvlink_logger.py 0 nvlink_usage.csv & 
echo "Done"

python tf_cnn_benchmarks.py --num_gpus=4 --batch_size=64 --model=resnet152_v2 --variable_update=replicated --data_dir=/home/ubuntu/imagenet

kill $(jobs -rp)

# for id in $(jobs -rp); do
# kill $id;
# done
