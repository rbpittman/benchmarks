#!/bin/bash

# echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &


echo "Starting nvlink logger...";
./nvlink_logger 0 &
echo "Done"

#resnet152_v2: bs <= 64
#resnet50    : bs <= 128

python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=128 --model=resnet50 --variable_update=replicated --all_reduce_spec=nccl --gradient_repacking=1

#--use_fp16=1
#--trace_file=traces/resnet50_bs128_8XV100_with_nccl_with_fp16_with_grad_repack_1.json

#--all_reduce_spec=nccl

#--data_dir=/home/ubuntu/imagenet

# for id in $(jobs -rp); do
# kill $id;
# done

kill `jobs -rp`;
