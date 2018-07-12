from __future__ import print_function
import re
from matplotlib import pyplot as plt
plt.rc('font', **{'size': 13})

f = open("inception3_bs128_with_fp16_testing_num_gpus.out", 'r')

y = []
pattern = re.compile(r'total images/sec: (\d+.\d+).*')
for line in f:
    match = re.match(pattern, line)
    if match:
        ips = float(match.groups()[0])
        y.append(ips)
f.close()


x = [1,2,4,8]
assert len(x) == len(y)
pos = list(range(4))
plt.bar(pos, y, 0.3, label="Tensorflow", align="center", color='g', linewidth=0)
ax = plt.gca()
# ax.grid(True)
ax.yaxis.grid()

plt.title("Tensorflow Inception-V3: Using fp-16, synthetic data, and NCCL")
plt.xlabel("Number of GPUs")
plt.xticks(pos, map(str, x))
plt.tick_params(top='Off', right='Off')
plt.ylabel("images/sec")

i = 0
for spine in plt.gca().spines.values():
    if i != 2:
        spine.set_visible(False)
    i += 1
plt.show()
