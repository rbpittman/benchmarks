#!/bin/bash

echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &
echo "Starting nvlink logger...";
python3 nvlink_logger.py 0.2 nvlink_usage.csv & 
echo "Done"

python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=64 --model=resnet50 --variable_update=replicated --data_dir=/home/ubuntu/imagenet

# for id in $(jobs -rp); do
# kill $id;
# done

kill $(jobs -rp);
