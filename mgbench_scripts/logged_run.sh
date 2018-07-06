#!/bin/bash
cd ~/mgbench/build

~/benchmarks/nvlink_logger 0 &


./halfduplex -size 10737418240 -from 1 -repetitions 1

kill $(jobs -rp)

exit 0;
