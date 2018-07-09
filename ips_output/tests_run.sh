#This file helps keep track of the test code that was run.

#resnet50 can only handle 128, it crashed for me at 256. 

#resnet50_8XV100_testing_bs.out
for BS in 16 32 64 128; do
    echo "auto-log-parser-reset ===========================";
    echo "LocalBS: $BS";
    python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=$BS --model=resnet50 --variable_update=replicated
done

for BS in 16 32 64 128; do
    echo "auto-log-parser-reset ===========================";
    echo "LocalBS: $BS";
    python tf_cnn_benchmarks.py --num_gpus=8 --batch_size=$BS --model=resnet50 --variable_update=replicated --all_reduce_spec=nccl
done


BS=128;
for NUM_GPUS in 1 2 4 8 16; do
    echo "auto-log-parser-reset ===========================";
    echo "LocalBS: $BS";
    python tf_cnn_benchmarks.py --num_gpus=$NUM_GPUS --batch_size=$BS --model=resnet50 --variable_update=replicated --all_reduce_spec=nccl
done
