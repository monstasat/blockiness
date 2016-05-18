#! /usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import matplotlib.pyplot as plot
from matplotlib import colors
import math
import os, sys
import timeit

# CONSTANTS
WH_LVL = 210
BL_LVL = 70

WH_DIFF = 4
GR_DIFF = 1

WH_DIFF_NOISE = 2
GR_DIFF_NOISE = 1

Knorm = 4

EXP = 2
CEIL = 0.7

L_DIFF = 6/8.


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Functions
#
wh_coef = []
gr_coef = []

def eval_coef():
    wh_coef = []
    gr_coef = []
    for x in range(1,101):
        x = x/100.
        wk = WH_DIFF*((2-x)**EXP)
        #wk = ((WH_DIFF/x - (WH_DIFF - 1))**EXP) + (WH_DIFF - 1)
        wk = math.ceil(wk - CEIL)
        #gk = ((GR_DIFF/x - (GR_DIFF - 1))**EXP) + (GR_DIFF - 1)
        gk = GR_DIFF*((2-x)**EXP)
        gk = math.ceil(gk - CEIL)
        wh_coef.append(wk)
        gr_coef.append(gk)
    wh_coef.insert(0, wh_coef[0]+1)
    gr_coef.insert(0, gr_coef[0]+1)
    return (wh_coef, gr_coef)

def plot_noise(noise, result_path, pic):
    # make cirillic font
    from matplotlib import rc
    font = {'family': 'Liberation Serif',
        'weight': 'normal'}
    rc('font', **font)

    fig, ax = plot.subplots()

    # construct plot
    z = np.array(noise)
    fig, ax = plot.subplots()
    im1 = ax.imshow(z, interpolation='nearest', vmin=0, vmax=1)
    bounds=[x/100. for x in range(0, 110, 10)]
    clrs = ['b','g','y','r']
    cmap = colors.ListedColormap(clrs)
    cbar = fig.colorbar(im1, boundaries=bounds, ticks=[x/100. for x in range(0, 110, 10)],
                        cmap=cmap)

    ax.set_title("Коэффициент детализации блоков")
    plot.xlabel('width')
    plot.ylabel('height')

    plot.savefig(str(os.path.join(result_path, pic + "_plot_noise.png")))

def plot_diff(diff, result_path, pic):
    # make cirillic font
    from matplotlib import rc
    font = {'family': 'Liberation Serif',
        'weight': 'normal'}
    rc('font', **font)

    # construct plot
    z = np.array(diff)
    fig, ax = plot.subplots()
    im1 = ax.imshow(z, interpolation='nearest', vmin=0, vmax=4)
    #bounds=[0,10,20,30,40,50,60,70,80,90,100]
    bounds=[(x/100.)*4 for x in range(0, 110, 10)]
    clrs = ['b','g','y','r']
    cmap = colors.ListedColormap(clrs)
    cbar = fig.colorbar(im1, boundaries=bounds, ticks=[(x/100.)*4 for x in range(0, 110, 10)],
                        cmap=cmap)

    ax.set_title("Заметность границ блоков")
    plot.xlabel('width')
    plot.ylabel('height')
    plot.savefig(str(os.path.join(result_path, pic + "_plot_diff.png")))

def grade(N):
    if N < 3:
        return 'Excellent'
    elif N < 20:
        return 'Acceptable'
    else:
        return 'Bad'
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Operators and test sequences
#
laplasian = [1, -2, 1, -2, 4, -2, 1, -2, 1]
laplasian_2 = [-1, -1, -1, -1, 8, -1, -1, -1, -1]
laplasian_3 = [0. -1, 0, -1, 4, -1, 0, -1, 0]
block_noisy = [0, 255]*32
block_smooth = [100, 120, 130, 140, 150, 160, 170, 180]*8
block_simple = [250]*64
block_random = [random.randint(0, 255) for i in range(64)]
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Classic blockiness detection algorithm implementation
#
def old_alg(x):
    Shb = .0
    Shnb = .0
    length = len(x)
    i = 4
    while i < length:
        sub = x[i-1] - x[i] if x[i-1] > x[i] else x[i] - x[i-1]
        subNext = x[i+1] - x[i] if x[i+1] > x[i] else x[i] - x[i+1]
        subPrev = x[i-2] - x[i-1] if x[i-2] > x[i-1] else x[i-1] - x[i-2]
        sumn = (1.0*subNext) + subPrev
        if (sumn == .0):
            sumn = 1.
        else:
            sumn = sumn / 2.0
        if ((i%8) != 0):
            Shnb += (1.0*sub)/sumn
        else:
            Shb += (1.0*sub)/sumn
        i += 4
    return Shb/Shnb
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Plain new blockiness detection algorithm implementation
# 
# Based on comparison of the average luminence values and noises of
# the blocks
#
def different_p(noise, lum):
    if lum > 4 and noise > 0.90:
        return True
    else:
        return False

def block_blob_alg(pic, width, height):
    w_blocks = int(width / 8)
    h_blocks = math.ceil(height / 8)
    length = len(pic)
    block_matrix = [0.0] * w_blocks*h_blocks
    block_avg_lum = [0.0] * w_blocks*h_blocks
    noise_result = [0.0] * w_blocks*h_blocks
    lum_result = [0.0] * w_blocks*h_blocks

    wl = 200
    bl = 50

    for y in range(height-1):
        for x in range(width-1):
            if ((x+1) % 8 != 0) and ((y+1) % 8 != 0):
                b_index = int(x / 8) + int(y / 8)*w_blocks
                cur = int(pic[x + y*width])
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                block_avg_lum[b_index] += cur
                if (cur < wl) or (cur > bl):
                    diff = bvc
                else:
                    diff = gvc
                if (abs(cur - right) >= diff):
                    block_matrix[b_index] += 1
                if (abs(cur - down) >= diff):
                    block_matrix[b_index] += 1

    block_matrix = list(map(lambda x: 1.0 - (x / (7.0*8.0*2.0)), block_matrix))
    block_avg_lum = list(map(lambda x: x / 64.0, block_avg_lum))
    #print(block_matrix)
    #print(block_avg_lum)
    for y in range(1, h_blocks-1):
        for x in range(1, w_blocks-1):
            b_index = x + y*w_blocks
            coef_noise = 0.0
            coef_lum = 0.0
            #print("Block:")
            #print(x, y)
            #print("vals:")
            for k,el in enumerate(laplasian):
                x_coord = int(k%3 - 1)
                y_coord = int(k/3) - 1
                index = b_index + y_coord*w_blocks + x_coord
                coef_lum += el*block_avg_lum[index]
                #coef_noise += block_matrix[index]
                #print(block_matrix[index])
            coef_lum = abs(coef_lum)
            #coef_noise = (abs(coef_noise) / 9.0)
            coef_noise = block_matrix[b_index]
            noise_result[b_index] = coef_noise
            lum_result[b_index] = coef_lum
            #result[b_index] = coef_lum
    #print(list(filter(lambda x: x >= 0.9, block_matrix)))
    #print(tmp_result)
    result = list(map(lambda x, y: different_p(x, y), noise_result, lum_result))
    return (result, w_blocks, h_blocks)
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Another new blockiness detection algorithm implementation
# 
# Based on comparison of the border luminance values and noises of
# the blocks
#

def get_vc(x, k_noise=1.0):
    if (x < WH_LVL) and (x > BL_LVL):
        val = gr_coef[int(k_noise*100)]
    else:
        val = wh_coef[int(k_noise*100)]
    return val

def border_diff_alg(pic, width, height):
    w_blocks = int(width / 8)
    h_blocks = math.ceil(height / 8)
    length = len(pic)
    # noise, right_diff, down_diff, right_diff_high, down_diff_high
    block_matrix = [[0.0, 0.0, 0.0] for x in range(w_blocks*h_blocks)]

    for y in range(1, height-2):
        for x in range(1, width-2):
            if ((x+1) % 8 != 0) and ((y+1) % 8 != 0) and ((x % 8) != 0) and ((y % 8) != 0):
                b_index = int(x / 8) + int(y / 8)*w_blocks
                cur = int(pic[x + y*width])
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                if (cur < WH_LVL) and (cur > BL_LVL):
                    diff = GR_DIFF_NOISE
                else:
                    diff = WH_DIFF_NOISE
                if ((x + 2) % 8 != 0):
                    if (abs(cur - right) >= diff):
                        block_matrix[b_index][0] += 1
                if ((y+2) % 8 != 0):
                    if (abs(cur - down) >= diff):
                        block_matrix[b_index][0] += 1

    block_matrix = list(map(lambda lst: [1.0 - (lst[0] / (6.*5*2)), 0, 0],
                            block_matrix))

    for y in range(height-8):
        for x in range(width-2):
            if ((x+1) % 8 == 0) or ((y+1) % 8 == 0):
                b_index = int(x / 8) + int(y / 8)*w_blocks
                cur = int(pic[x + y*width])
                left = int(pic[(x-1) + y*width])
                top = int(pic[x + (y-1)*width])
                right = int(pic[(x+1) + y*width])
                right1 = int(pic[(x+2) + y*width])
                down = int(pic[x + (y+1)*width])
                down1 = int(pic[x + (y+2)*width])
                if ((x+1) % 8 == 0):
                    diff = get_vc(cur, max(block_matrix[b_index][0], block_matrix[b_index+1][0]))
                    denom = round((abs(left-cur) + abs(right-right1))/Knorm)
                    norm = abs(right - cur) / denom if (denom > 0) else abs(right - cur)
                    if norm > diff:
                        block_matrix[b_index][1] += 1

                    #if int(x/8) == 19 and int(y/8) == 50:
                    #    print("x: ", x%8, "| y: ", y%8, "| x tol: ", diff, "| x denom:", denom, "| x diff: ", abs(right - cur), "| x normed: ", norm)
                if ((y+1) % 8 == 0):
                    diff = get_vc(cur, max(block_matrix[b_index][0], block_matrix[b_index+int(width/8)][0]))
                    denom = round((abs(top-cur) + abs(down-down1))/Knorm)
                    norm = abs(down - cur) / denom if (denom > 0) else abs(down - cur)
                    if norm > diff:
                        block_matrix[b_index][2] += 1

                    #if int(x/8) == 19 and int(y/8) == 50:
                    #    print("x: ", x%8, "| y: ", y%8, "| cur: ", cur, "| down: ", down, "| y tol: ", diff, "| y denom:", denom, "| y diff: ", abs(down - cur), "| y normed: ", norm)

    # normalising matrix
    block_matrix = list(map(lambda lst: [lst[0], lst[1]/8.0, lst[2]/8.0],
                            block_matrix))

    return (block_matrix, w_blocks, h_blocks)

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


#file_names = ["lena.tif", "5.jpg", "baby.JPG.bmp"]
#file_names = ["0.jpg", "1.jpg", "2.jpg", "3.jpg", "9.jpg"]
#file_names = ["9.jpg"]
#file_names = ["0.jpg", "baby.JPG.bmp", "lena.tif", "5.jpg", "b1.bmp", "9.jpg"]
#file_names = ["mri.tif", "einstein.tif", "lena.tif"]
#file_names = ["lena.tif"]
#file_names = ["b1.bmp"]

def main(path, pics):
    global wh_coef
    global gr_coef
    wh_coef, gr_coef = eval_coef()

    for pic in pics:
        result_path = os.path.join(path, "results")
        if not (os.path.exists(result_path)):
            os.mkdir(result_path)
        img = Image.open(str(os.path.join(path, pic))).convert("YCbCr")
        img.convert("L").save(str(os.path.join(result_path, pic + "_Y.bmp")), "BMP")
        arr = np.array(img)
        Y = arr[:,:,0]
        height = len(Y)
        width = len(Y[0])
        Y = np.concatenate(Y)

        def wrapper(func, *args, **kwargs):
            def wrapped():
                return func(*args, **kwargs)
            return wrapped

        #wrapped = wrapper(old_alg, Y)
        #old_time = timeit.timeit(wrapped, number=1)
        #print("old alg time: ", old_time)

        #wrapped = wrapper(border_diff_alg, Y, width, height)
        #new_time = timeit.timeit(wrapped, number=1)
        #print("new alg time: ", new_time)

        #print("new time/old time: ", new_time/old_time)

        result, wb, hb = border_diff_alg(Y, width, height)
        result_old = old_alg(Y)

        img = img.convert("RGBA")
        i = 0+wb
        counter = 0
        while i < len(result)-wb:
            noise = result[i][0]
            borders = [result[i][1], result[i][2], result[i-1][1], result[i - wb][2]]
            x = int(i % wb)
            y = int(i / wb)
            if x == 19 and y == 50:
            #if x == 32 and y == 58:
                #print("borders: ", borders)
                #print("noise: ", result[i][0])
                x = int(i % wb)*8
                y = int(i / wb)*8
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+7, y+7], fill=None, outline=(0x00, 0xff, 0x00))
                del draw
            if len(list(filter(lambda x: x >= L_DIFF, borders))) >= 2: #or
                x = int(i % wb)*8
                y = int(i / wb)*8
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+7, y+7], fill=None, outline=(0xff, 0x00, 0x00))
                del draw
                counter += 1
            i += 1

        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (170, 16)], fill=(255,255,255,255), outline=None)
        fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 12)

        blck_perc = (100.0*counter) / ((wb-2)*(hb-2))
        text = "Выделено блоков: " + ('%.2f%%' % blck_perc)
        draw.text((0, 0), text, font=fnt, fill=(0,0,0))
        del draw
        img.save(str(os.path.join(result_path, pic + "_result.png")), "PNG")
        #img.show()
        # plotting the result
        i = 0
        noise_matrix = []
        diff_matrix = []
        f = open('diff', 'w')
        while i < len(result)/wb:
            j = 0
            tmp_noise = []
            tmp_diff = []
            cnt = 0
            while j < wb:
                up_diff = 0
                down_diff = result[i*wb + j][2]
                left_diff = 0
                right_diff = result[i*wb + j][1]
                if i > 1:
                    up_diff = result[(i-1)*wb + j][2]
                if j > 1:
                    left_diff = result[i*wb + j - 1][1]
                borders = [up_diff, down_diff, left_diff, right_diff]
                tmp_noise.append(1. - (result[i*wb + j][0]))
                tmp_diff.append(sum(borders))
                f.write("%.2f " % (sum(borders)))
                j += 1
            noise_matrix.append(tmp_noise)
            diff_matrix.append(tmp_diff)
            f.write("\n")
            i += 1
        f.close()
        # noise:
        plot_noise(noise_matrix, result_path, pic)
        # difference
        plot_diff(diff_matrix, result_path, pic)

        percent = (100.0*counter) / ((wb-2)*(hb-2))

        print(pic + "\told_alg: " + str(result_old) + "\tnew_alg: " + str(percent) + "% "+ grade(percent))
        

if __name__ == "__main__":
    args = sys.argv
    if (len(args) < 3):
        print("Usage: " + args[0] + " /path/to/folder picture.ext picture2.ext pictureN.ext")
        exit(1)
    main(args[1], args[2:])
