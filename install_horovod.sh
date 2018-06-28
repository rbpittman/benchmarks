#!/bin/bash
HOROVOD_NCCL_HOME=/lib/nccl/cuda-9.0 HOROVOD_GPU_ALLREDUCE=NCCL pip install --no-cache-dir horovod
