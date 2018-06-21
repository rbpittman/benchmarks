#!/bin/bash

# Run the following commands on host_1 (10.0.0.2): 172.31.7.145

#!/bin/bash
H1=172.31.5.238
H2=172.31.5.43

if [ -z $1 ]; then
    echo "Need job name (worker/ps)";
    exit 1;
else
    JOB_NAME=$1
fi

ifconfig | grep ${H1} > /dev/null
if [ "$?" -eq 0 ]; then
    TASK_INDEX=0;
else
    TASK_INDEX=1;
fi

echo "Job name: $JOB_NAME";
echo "Task index: $TASK_INDEX";
python3 tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=1 --batch_size=64 --model=resnet50 --variable_update=distributed_replicated --job_name=${JOB_NAME} --ps_hosts=${H1}:50000,${H2}:50000 --worker_hosts=${H1}:50001,${H2}:50001 --task_index=${TASK_INDEX}



