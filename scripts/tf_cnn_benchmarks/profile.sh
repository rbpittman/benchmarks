#!/bin/bash

#nvprof --unified-memory-profiling off --metrics sm_efficiency python3 tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --variable_update=parameter_server

mkdir -p train_dir

python3 tf_cnn_benchmarks.py --data_format=NCHW --batch_size=32 \
       --model=resnet50 --optimizer=momentum --variable_update=replicated \
       --gradient_repacking=1 --num_gpus=8 \
       --num_epochs=1 --weight_decay=1e-4 --use_fp16 \
       --train_dir=./train_dir --display_every=1

#--trace_file=1X_K80_resnet50.json 
