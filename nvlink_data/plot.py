import matplotlib.pyplot as plt
import csv

reader = csv.reader(open("parameter_server.csv", 'r'))
data = [[float(x) for x in line] for line in reader]

slope_data = []
for i in range(1, len(data)):
    entry1 = data[i-1]
    entry2 = data[i  ]
    elapsed_time = entry2[0] - entry1[0]
    new_line = [entry2[0], (entry2[1] - entry1[1]) / elapsed_time, (entry2[2] - entry1[2]) / elapsed_time]
    slope_data.append(new_line)

x, y1, y2 = [[row[i] for row in slope_data] for i in range(3)]
plt.plot(x, y1)
plt.xlim()
plt.show()
