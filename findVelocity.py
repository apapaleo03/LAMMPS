
####################################################################

import tkinter
from tkinter.filedialog import askdirectory
import numpy as np
import pandas as pd
import re
from os import listdir
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from scipy.stats import linregress


################### Tkinter Set-up ######################
#                   --------------

root = tkinter.Tk()
root.wm_title("Log Analysis")

################### Figure Set-up ######################
#                   --------------

fig = Figure(figsize=(10, 4), dpi=100)
ax = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

canvas = FigureCanvasTkAgg(fig, master=root) 
canvas.draw()
canvas.get_tk_widget().grid(row=3,column=3)

toolbarFrame= tkinter.Frame(master=root)
toolbarFrame.grid(row=8,column=3)

toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()


################### Global Variables ######################
#                   --------------

file_loaded = False
fileName = ''
directory = ''
xdata = 0
ydata = 0
curr_temp = 0
temp_axis = []
slope_axis = []
data = {}

################ Key Press for Some Reason #################
#                --------------------------

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)
canvas.mpl_connect("key_press_event", on_key_press)

##################### Quit The Window ######################
#                    -----------------

def _quit():
    root.quit()     
    root.destroy()  

quit_button = tkinter.Button(master=root, text="Quit", command=_quit)

############ Read file and update param options #############
#            ----------------------------------

choices = (' ')
var = tkinter.StringVar(root)
var.set('')
param_options = tkinter.OptionMenu(root,var,*choices)
def callback(*args):
    global curr_temp
    global fileName
    fileName = var.get()
    plot()
    orient,temp,run = [s for s in re.findall(r'-?\d+\.?\d*', var.get())]
    curr_temp = -1*float(temp)
var.trace('w',callback)


def read_lengths():
    global directory
    global file_loaded
    global curr_temp
    file_loaded = True
    directory = askdirectory()
    files = sorted(listdir(directory))
    orient,temp ,run= [s for s in re.findall(r'-?\d+\.?\d*', files[0])]
    curr_temp = -1*float(temp)

    var.set(files[0])
    param_options['menu'].delete(0,'end')
    for param in files:
        param_options['menu'].add_command(label=param, command=tkinter._setit(var,param))
        

file_button = tkinter.Button(master=root, text="Choose Directory", command=read_lengths)

#################### Plot the data ######################
#                   --------------
    
def plot():
    global file_loaded
    global xdata
    global ydata
    if file_loaded:
        ax.cla()
        step,lz = np.loadtxt(directory+'/'+var.get(),float,unpack=True)

        xdata = step*0.000001
        ydata = lz
        ax.plot(xdata,ydata)
        ax.set_title(var.get()+' vs. Step')
        ax.set_xlabel('Step')
        ax.set_ylabel('Lz')
        canvas.draw()

plot_button = tkinter.Button(root,text="Plot",command=plot)

################### Span Selector ######################
#                   -------------

def onselect(xmin, xmax):
    if file_loaded:
        plot()
        indmin, indmax = np.searchsorted(xdata, (xmin, xmax))
        indmax = min(len(xdata) - 1, indmax)

        thisx = xdata[indmin:indmax]
        thisy = ydata[indmin:indmax]
        slope, intercept, r, p, std = linregress(thisx,thisy)
        ax.plot(thisx,thisx*slope+intercept)
        data[fileName] = [curr_temp,slope*(-1)]
        print(data)
        x_ax , y_ax = zip(*data.values())
        ax2.cla()
        ax2.scatter(x_ax,y_ax)
        ax2.set_xlim(330,350)
        fig.canvas.draw()

# Set useblit=True on most backends for enhanced performance.
span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'))

##################### Placements ########################
#                     ----------

plot_button.grid(row=6,column=5)
quit_button.grid(row=7,column=3)
param_options.grid(row=6,column=1)
file_button.grid(row=6,column=3)

#------------------------------------------------------#


            

tkinter.mainloop()
