#!/bin/bash
H1=172.31.91.238
H2=172.31.93.217


ifconfig | grep ${H1} > /dev/null
if [ "$?" -eq 0 ]; then
    TASK_INDEX=0;
else
    TASK_INDEX=1;
fi

run() {
    python3 tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=2 \
	    --batch_size=32 --model=resnet50 --variable_update=distributed_replicated \
	    --job_name=${1} --ps_hosts=${H1}:50000,${H2}:50000 \
	    --worker_hosts=${H1}:50001,${H2}:50001 --task_index=${TASK_INDEX}
}

run ps &
run worker
kill $(jobs -p)
