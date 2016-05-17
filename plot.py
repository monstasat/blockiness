import re
import matplotlib.pyplot as plt
import numpy as np

POINTS = 50
START = 0
STOP = START + POINTS

def get_data():
    f = open("result.temp", "r")
    s = f.read()
    s_arr = s.split("\n")

    data = []
    dmos_arr = []
    new_arr = []
    old_arr = []
    for i in range(0, len(s_arr), 6):
        group = s_arr[i+1:i+6]
        if len(group) > 0:
            pic_name = group[0]
            dmos = float(re.findall("\d+\.\d+", group[1])[0])
            old = float(re.findall("\d+\.\d+", group[2])[0])
            new = float(re.findall("\d+\.\d+", group[3])[0])

            dmos_arr.append(dmos)
            new_arr.append(new)
            old_arr.append(old if old <= 100 else 100)
            data.append([dmos, old, new])

    plt.plot([x for x in range(len(dmos_arr[START:STOP]))], dmos_arr[START:STOP])
    plt.plot([x for x in range(len(new_arr[START:STOP]))], new_arr[START:STOP])
    plt.plot([x for x in range(len(old_arr[START:STOP]))], old_arr[START:STOP])
    plt.legend(['dmos', 'new alg', 'old alg'])
    plt.xlabel('picture', fontsize=18)
    plt.ylabel('result', fontsize=18)
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.yticks(np.arange(0, 100+5, 5))
    plt.xticks(np.arange(0, POINTS+5, 5))
    plt.show()


get_data()
