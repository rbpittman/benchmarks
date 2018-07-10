from __future__ import print_function

import json, re
from matplotlib import pyplot as plt

filename = "resnet50_bs128_8XV100_with_nccl.json"

with open(filename, 'r') as f:
    data = json.load(f)

i = 0
events = data["traceEvents"]
# alloc_names = {}

gpu_totals = [0] * 8

allocs_for_gpu0 = []

# total_bytes = 0
bytes_pattern = re.compile(r'.*requested_bytes: (\d+).*', re.MULTILINE|re.DOTALL)
alloc_name_pattern = re.compile(r'.*allocator_name: ([^\s]+).*', re.MULTILINE|re.DOTALL)
for event in events:
    name = event["name"]
    if "nccl" in name.lower():
        ph = event["ph"]
        if ph == 'O':
            desc = event["args"]["snapshot"]["tensor_description"]
            bytes_match = re.match(bytes_pattern, desc)
            alloc_name_match = re.match(alloc_name_pattern, desc)
            assert bytes_match != None
            assert alloc_name_match != None
            num_bytes = int(bytes_match.groups()[0])
            alloc_name = alloc_name_match.groups()[0]
            gpu_i = int(alloc_name[4])
            if gpu_i == 0:
                allocs_for_gpu0.append(num_bytes)
                # total_bytes += num_bytes
                
            gpu_totals[gpu_i] += num_bytes

# for key in alloc_names:
#     print(key, alloc_names[key])
# print(total_bytes, "bytes")
# print(total_bytes/float(2**20), "MB")
# for b in gpu_totals:
#     print(b/float(2**20))

plt.hist(allocs_for_gpu0, 100, linewidth=0)
plt.title("Histogram of the number of bytes for NCCL operations (resnet50)")
plt.xlabel("bytes")
plt.ylabel("count")

# trimmed_allocs = [alloc for alloc in allocs_for_gpu0 if alloc <= 10000]
# print(trimmed_allocs)
# plt.hist(trimmed_allocs, 100, linewidth=0)

plt.show()

# for key in ph_values:
#     print(key)

"""
D = Deletion
O = object snapshot
N = object creation
s = flow start
t = flow end
X = region event
"""
