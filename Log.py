import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import scipy.stats as sci
import sys


def read_log():
    if len(sys.argv) < 2:
        print('** read_log.py needs the following command line arguments:\n\n'+
                '\t\t LAMMPS log file \n \t\t LAMMPS timestep info')
        filename = input('Enter Filename:')
        timestep = float(input('Enter Timestep:'))
    else:
        filename = sys.argv[1]
        timestep = float(sys.argv[2])

    with open(filename) as data:
            header = []
            log = []
            run = 0
            start = False
            first = True
            Production = False
            Prod_run = 0
            for line in data.readlines():
                line = line.split()
                line = line[0:12]
                if len(line) != 0:
                    if line[0] == 'Step':
                        start = True
                        run +=1
                        if first:
                            header = line
                            first = False
                        continue
                    elif line[0] == 'Loop':
                        start = False
                    if line[0] == 'run':
                        if 'every' in line:
                            Production = True
                    if start:
                        if Production:
                            log.append(line)
        
    log = np.asarray(log).astype(float)

    df_log = pd.DataFrame(data = log, columns = header)
    df_log['Step'] = df_log['Step']*timestep


    fig, ax = plt.subplots()
    ax.autoscale(enable=True,axis='both')
    l, = ax.plot(df_log['Step'], df_log['Step'])
    plt.subplots_adjust(left=0.3,right=0.7)
    ave_title = fig.text(0.77,0.3,'Average Value:')
    ave = fig.text(0.78,0.25,'')
    slope_title = fig.text(0.77,0.2,'Slope:')
    slope_disp = fig.text(0.78,0.15,'')


    axcolor = 'whitesmoke'
    ############################################################

    fig.text(0.8,0.91,'X-axis',fontsize=12)
    rax = plt.axes([0.75,0.4, 0.15,0.5], facecolor=axcolor)
    radio_x = RadioButtons(rax,header)

    def xfunc(label):
        ax.cla()
        xdata = df_log[label]
        ydata = df_log[radio_y.value_selected]
        l, = ax.plot(xdata, ydata)
        slope_disp.set_text('')
        ax.grid(True)
        plt.draw()

    radio_x.on_clicked(xfunc)

    #############################################################
    fig.text(0.1,0.91,'Y-axis',fontsize=12)
    rax = plt.axes([0.05, 0.4, 0.15, 0.5], facecolor=axcolor)
    radio_y = RadioButtons(rax, header)

    def yfunc(label):
        ax.cla()
        xdata = df_log[radio_x.value_selected]
        ydata = df_log[label]
        l, = ax.plot(xdata, ydata)
        ax.grid(True)
        ave.set_text(str(round(df_log[label].mean(),3)))
        slope_disp.set_text('')
        plt.draw()

    radio_y.on_clicked(yfunc)


    #############################################################
    fig.text(0.1,0.31,'Hist',fontsize=12)
    rax = plt.axes([0.05, 0.1, 0.15, 0.2], facecolor=axcolor)
    radio_h = RadioButtons(rax, ('Pxx','Pyy','Pzz'))

    def histfunc(label):
        ax.cla()
        ydata = df_log[label]
        ax.hist(ydata,100)
        ax.grid(True)
        slope_disp.set_text('')
        plt.draw()

    radio_h.on_clicked(histfunc)


    while 1:

        if plt.waitforbuttonpress():

            pts = np.asarray(plt.ginput(2, timeout=-1))
        
            p1 = pts[0][0]
            p2 = pts[1][0]


            found_p1 = False

            
            for i in range(len(df_log[radio_x.value_selected])):
                if df_log[radio_x.value_selected][i] > p1 and not found_p1:
                    mini = i
                    found_p1 = True

                if df_log[radio_x.value_selected][i] > p2:
                    maxi = i  
                    break   

            slope, intercept, r, p, std = sci.linregress(df_log[radio_x.value_selected][mini:maxi],
                                                        df_log[radio_y.value_selected][mini:maxi])
            ph1 = ax.plot(df_log[radio_x.value_selected][mini:maxi],
                            df_log[radio_x.value_selected][mini:maxi]*slope+intercept, 'r')
            slope_disp.set_text(str(round(slope,3)))


            if plt.waitforbuttonpress():
                break

            for p in ph1:
                p.remove()

    plt.show()