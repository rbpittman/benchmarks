#!/bin/bash

# echo "Starting net logger...";
# python3 net_logger.py 0.2 net_usage.csv &
echo "Starting nvlink logger...";
./nvlink_logger 0 &
echo "Done"

MODEL=resnet152_v2
BS=64

#python tf_cnn_benchmarks.py --num_gpus=4 --batch_size=64 --model=resnet152_v2 --variable_update=replicated --trace_file=trace.json
python tf_cnn_benchmarks.py --num_gpus=4 --batch_size=${BS} --model=${MODEL} --summary_verbosity=0 --trace_file=trace_${MODEL}_${BS}.json

#--data_dir=/home/ubuntu/imagenet

kill $(jobs -rp)

# for id in $(jobs -rp); do
# kill $id;
# done
