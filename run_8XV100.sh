#!/bin/bash

# echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &


# echo "Starting nvlink logger...";
# ./nvlink_logger 0 &
# echo "Done"

BS=64;
for model in resnet50 resnet152_v2 inception3 vgg19; do
    echo "auto-log-parser-reset ===========================";
    echo "LocalBS: $BS";
    python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=$BS --model=$model --variable_update=replicated --all_reduce_spec=nccl
done

#--data_dir=/home/ubuntu/imagenet

# for id in $(jobs -rp); do
# kill $id;
# done

kill `jobs -rp`;
