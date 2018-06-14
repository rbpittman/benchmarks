#!/bin/bash
python3 tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=2 \
       --batch_size=32 --model=resnet50 --variable_update=distributed_replicated \
       --job_name=worker --ps_hosts=172.31.8.57:50000,172.31.7.145:50000 \
       --worker_hosts=172.31.8.57:50001,172.31.7.145:50001 --task_index=0 --trace_file=2X_IP_K80_resnet50.json --display_every=1
