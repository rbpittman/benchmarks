#!/bin/bash

#nvprof --unified-memory-profiling off --metrics sm_efficiency python3 tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --variable_update=parameter_server

VARIABLE_UPDATE=parameter_server
python3 tf_cnn_benchmarks.py --data_format=NCHW --batch_size=32 \
       --model=resnet50 --optimizer=momentum --variable_update=$VARIABLE_UPDATE \
       --gradient_repacking=8 --num_gpus=8 \
       --num_batches=10 --weight_decay=1e-4 --use_fp16 \
       --display_every=1 --local_parameter_device=cpu \
       --trace_file=traces/var_update_${VARIABLE_UPDATE}_cpu_K80.json \
#       --train_dir=./train_dir
