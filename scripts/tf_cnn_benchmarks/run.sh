#!/bin/bash

# Run the following commands on host_0 (10.0.0.1): 172.31.8.57
python3 tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=2 \
       --batch_size=64 --model=resnet50 --variable_update=distributed_replicated \
       --job_name=worker --ps_hosts=172.31.8.57:50000,172.31.7.145:50000 \
       --worker_hosts=172.31.8.57:50001,172.31.7.145:50001 --task_index=0

python3 tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=2 \
       --batch_size=64 --model=resnet50 --variable_update=distributed_replicated \
       --job_name=ps --ps_hosts=172.31.8.57:50000,172.31.7.145:50000 \
       --worker_hosts=172.31.8.57:50001,172.31.7.145:50001 --task_index=0

# Run the following commands on host_1 (10.0.0.2): 172.31.7.145
