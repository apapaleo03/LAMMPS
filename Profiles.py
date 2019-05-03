import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import subprocess

dir = '100/'
name = 'temp100-0.6'
def create(dir,name, plot = False):
    with open(dir+'Profile/'+name+'.profile') as dat:
        data = [line.split() for line in dat.readlines() if line.split()[0] != '#' and len(line.split()) != 3]

    allData = []
    first = True
    for datum in data:
        if datum[0] == '1':
            if first:
                dum = []
                dum.append(datum)
                first = False
                continue
            else:
                allData.append(dum)
                dum = []
                dum.append(datum)
                continue
        dum.append(datum)

    mins = min([len(datum) for datum in allData])

    # Need all dims to be same length for np initialization
    for i in range(len(allData)):
        allData[i] = allData[i][0:mins]

    allData = np.array(allData).astype(float)

    if plot:
        plt.figure(figsize = (20,10))
        plt.plot(allData[int(len(allData)/2)][:,1],allData[int(len(allData)/2)][:,-1])
        plt.show()

    return allData

def mov(dir,name,datas,datas2 = []):
    # Fixing random state for reproducibility
    np.random.seed(19680801)

    files = []
    xmin = min(datas[1][:,1])
    xmax = max(datas[1][:,1])
    xbuf = 10
    ymin = min(datas[1][:,-1])
    ymax = max(datas[1][:,-1])
    ybuf = 0.1
    fig, ax = plt.subplots(figsize = (20,10))

    for i in range(len(datas)):
        plt.cla()
        plt.xlim(xmin-xbuf, xmax+xbuf)
        plt.ylim(ymin-ybuf, ymax+ybuf)
        plt.plot(datas[i][:,1],datas[i][:,-1])
        plt.scatter(datas[i][:, 1], datas[i][:, -1])
        if datas2:
            plt.plot(datas2[i][:, 1], datas2[i][:, -1])
            plt.scatter(datas2[i][:, 1], datas2[i][:, -1])
        plt.grid()
        fname = '_tmp%03d.png' % i
        plt.savefig(fname)
        files.append(fname)

    print('Making movie animation.mpg - this may take a while')
    subprocess.call("mencoder 'mf://_tmp*.png' -mf type=png:fps=5 -ovc lavc "
                    "-lavcopts vcodec=wmv2 -oac copy -o "+dir+"Videos/"+name+".mpg",shell = True)

    #cleanup
    for fname in files:
        os.remove(fname)
    print('Done!')


def allMov(dir,observables, temperatures):
    for obs in observables:
        for temp in temperatures:
            name = obs+dir.replace('/','-')+temp
            print(name+' is Starting...')
            datas= create(dir,name)
            mov(dir,name,datas)




