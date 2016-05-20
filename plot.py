import re
import matplotlib.pyplot as plt
import numpy as np
import math

POINTS = 16
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

    plt.plot([x for x in range(1, len(dmos_arr[START:STOP])+1)], dmos_arr[START:STOP])
    plt.plot([x for x in range(1, len(new_arr[START:STOP])+1)], new_arr[START:STOP])
    plt.plot([x for x in range(1, len(old_arr[START:STOP])+1)], old_arr[START:STOP])
    plt.legend(['DMOS', 'Разработанный алгоритм', 'R.Muijs, I.Kirenko'])
    plt.xlabel('Изображение', fontsize=18)
    plt.ylabel('Результат', fontsize=18)
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.yticks(np.arange(0, 100+5, 5))
    plt.xticks(np.arange(1, POINTS, 1))
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
    for x in range(0, 1000, 1):
        x = x/1000.
        x_arr.append(x)
        wk = (1/(1-x)) + (WH_DIFF -1) + (x)*N
        gk = (1/(1-x)) + (GR_DIFF -1) + (x)*N
        wh_coef.append(wk)
        gr_coef.append(gk)
        wk = (1/(1-x)) + (WH_DIFF -1) + (x)*2
        gk = (1/(1-x)) + (GR_DIFF -1) + (x)*2
        wh_coef_2.append(wk)
        gr_coef_2.append(gk)
        wk = (1/(1-x)) + (WH_DIFF -1) + (x)*4
        gk = (1/(1-x)) + (GR_DIFF -1) + (x)*4
        wh_coef_3.append(wk)
        gr_coef_3.append(gk)
    wh_coef.insert(0, wh_coef[0]+1)
    gr_coef.insert(0, gr_coef[0]+1)
    wh_coef_2.insert(0, wh_coef_2[0]+1)
    gr_coef_2.insert(0, gr_coef_2[0]+1)
    wh_coef_3.insert(0, wh_coef_2[0]+1)
    gr_coef_3.insert(0, gr_coef_2[0]+1)
    x_arr.insert(0,0)

    plt.plot(x_arr, gr_coef, linestyle='-', color='red', label='lol')
    plt.plot(x_arr, wh_coef, linestyle='-', color='blue')
    plt.plot(x_arr, gr_coef_3, color='red', linestyle='--')
    plt.plot(x_arr, wh_coef_3, color='blue', linestyle='--')
    plt.ylim([0, 20])
    plt.xlim([0,1])
    plt.xlabel(r"$K_d$", fontsize=24)
    plt.ylabel(r"$L_{vw}$", fontsize=24)
    plt.xticks(np.arange(0, 1.1, 0.1), fontsize=14)
    plt.yticks(np.arange(0, 21, 1), fontsize=14)
    plt.legend([r'$L_v=2$, $n=0$', r'$L_v=6$, $n=0$',
                r'$L_v=2$, $n=4$', r'$L_v=6$, $n=4$'],
                fontsize=18,
                loc=2)
    plt.grid(b=True, which='both', color='0.65',linestyle='-')
    plt.show()

plot_results()
#plot_kw()
