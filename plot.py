import re
import matplotlib.pyplot as plt
import numpy as np
import math

POINTS = 50
START = 0
STOP = START + POINTS

# make cirillic font
from matplotlib import rc
font = {'family': 'Liberation Serif',
        'weight': 'normal'}
rc('font', **font)

def plot_results():
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

def plot_kw():
    WH_DIFF = 6
    GR_DIFF = 2
    CEIL = 0.2
    N = 0
    wh_coef = []
    gr_coef = []
    wh_coef_2 = []
    gr_coef_2 = []
    wh_coef_3 = []
    gr_coef_3 = []
    x_arr = []
    for x in range(1, 1100, 1):
        x = x/1000.
        x_arr.append(x)
        wk = (1/x) + (WH_DIFF -1) + (1-x)*N
        gk = (1/x) + (GR_DIFF -1) + (1-x)*N
        wh_coef.append(wk)
        gr_coef.append(gk)
        wk = (1/x) + (WH_DIFF -1) + (1-x)*2
        gk = (1/x) + (GR_DIFF -1) + (1-x)*2
        wh_coef_2.append(wk)
        gr_coef_2.append(gk)
        wk = (1/x) + (WH_DIFF -1) + (1-x)*4
        gk = (1/x) + (GR_DIFF -1) + (1-x)*4
        wh_coef_3.append(wk)
        gr_coef_3.append(gk)
    wh_coef.insert(0, wh_coef[0]+1)
    gr_coef.insert(0, gr_coef[0]+1)
    wh_coef_2.insert(0, wh_coef_2[0]+1)
    gr_coef_2.insert(0, gr_coef_2[0]+1)
    wh_coef_3.insert(0, wh_coef_2[0]+1)
    gr_coef_3.insert(0, gr_coef_2[0]+1)
    x_arr.insert(0,0)

    plt.plot(x_arr, gr_coef)
    plt.plot(x_arr, wh_coef)
    plt.plot(x_arr, gr_coef_2)
    plt.plot(x_arr, wh_coef_2)
    plt.plot(x_arr, gr_coef_3)
    plt.plot(x_arr, wh_coef_3)
    plt.ylim([0, 20])
    plt.xlim([0,1])
    plt.legend(['Серый пиксель, N=0', 'Тёмный/Яркий пиксель, N=0',
                'Серый пиксель, N=2', 'Тёмный/Яркий пиксель, N=2',
                'Серый пиксель, N=4', 'Тёмный/Яркий пиксель, N=4'])
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.show()

#plot_results()
plot_kw()
