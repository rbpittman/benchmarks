#!/bin/bash
cd ~/mgbench/build

~/benchmarks/nvlink_logger 0 &


./halfduplex -size 1073741824 -repetitions 1

kill $(jobs -rp)

exit 0;
