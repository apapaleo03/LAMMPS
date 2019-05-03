import time
import scipy.stats as sci
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isdir
import re


def write_slope_data(orientation,slopes):
    """
    Writes the data in the slopes parameter to a file
    :param orientation: orientation of the system
    :param slopes: array containing the slopes obtained from linregress
    :return:
    """

    with open(orientation+'/'+ orientation + '_slopes.txt', 'w') as fil:
        fil.write("# " + orientation+'\n')

        for dat in slopes:
            fil.write(str(dat[0]) + ' ' + str(dat[1])+'\n')

def get_temp(file):
    """
    Returns the temperature of the file
    :param file: the file of which the temperature will be obtained
    :return: temperature
    """
    specs = [s for s in re.findall(r'-?\d+\.?\d*', file)]
    return specs[0].replace('-',''), abs(float(specs[-1]))


def instruct(s):
    print(s)
    plt.title(s, fontsize=12)
    plt.draw()


def Lvt(dir):
    isDirectory = False
    if isdir(dir):
        files = sorted(listdir(dir))
        step, lz = np.loadtxt(dir+files[0],float,unpack = True)
        isDirectory = True
    else:
        files = [dir.split('/')[-1]]
        step, lz = np.loadtxt(dir,float,unpack = True)
    step = step*0.000001
    plt.figure(figsize=(12,8))
    plt.clf()
    plt.axis([np.min(step), np.max(step), np.min(lz), np.max(lz)])
    plt.setp(plt.gca(), autoscale_on=True)
    slopes = []


    for file in files:
        instruct('Select points to calculate slope')
        if isDirectory:
            step, lz = np.loadtxt(dir+file,float,unpack = True)
        else:
            step, lz = np.loadtxt(dir,float,unpack = True)
        step = step*0.000001
        l1 = plt.plot(step,lz)
        orientation, temp = get_temp(file)

        while True:
            pts = []

            while len(pts) < 2:
                instruct('Select 2 points with mouse')
                pts = np.asarray(plt.ginput(2, timeout=-1))

                if len(pts) < 2:
                    instruct('Too few points, starting over')
                    time.sleep(1)  # Wait a second

            p1 = pts[0][0]
            p2 = pts[1][0]

            for i in range(len(step)):
                if step[i] > p1:
                    mini = i
                    break

            for i in range(len(step)):
                if step[i] > p2:
                    maxi = i  
                    break   

            slope, intercept, r, p, std = sci.linregress(step[mini:maxi],lz[mini:maxi])
            slopes.append([slope,temp])
            ph = plt.plot(step[mini:maxi], step[mini:maxi]*slope+intercept, 'k')
            print(slope)

            instruct('Press enter to continue, or click to pick again')

            if plt.waitforbuttonpress():
                break

            # Get rid of fill
            for p in ph:
                p.remove()

    write_slope_data(orientation,slopes)

    plt.title('Test')
    plt.xlabel(r'$Time\; [ns]$', fontsize=14)
    plt.ylabel(r'$Length\: [\AA]}$',fontsize=14)
    plt.savefig('fig')



