#!/bin/bash

# Run the following commands on host_1 (10.0.0.2): 172.31.7.145

#!/bin/bash
H1=172.31.3.196
H2=172.31.1.249

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

if [ "$JOB_NAME" = "worker" ]; then
    echo "Starting net logger...";
    python3 net_logger.py 1 net_usage.csv &
    echo "Done"
fi

echo "Launching training"
python tf_cnn_benchmarks.py --local_parameter_device=gpu --num_gpus=4 --batch_size=128 --model=resnet50 --variable_update=distributed_replicated --job_name=${JOB_NAME} --ps_hosts=${H1}:50000,${H2}:50000 --worker_hosts=${H1}:50001,${H2}:50001 --task_index=${TASK_INDEX} --allow_growth=1 --num_batches=200
