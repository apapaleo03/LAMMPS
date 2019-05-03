
####################################################################

import tkinter
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from scipy.stats import linregress
from matplotlib.widgets import SpanSelector
#######################################################
root = tkinter.Tk()
root.wm_title("Log Analysis")
#######################################################
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.scatter([1,1,1,1,1,1,1,1,1,1.5,2,2.5,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,6],
            [5,4.5,4,3.5,3,2.5,2,1.5,1,3,3,3,5,4.5,4,3.5,3,2.5,2,1.5,1,4,3,2.5,2,1.5,1,1])
#######################################################

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().grid(row=3,column=3)#,rowspan=3,columnspan=5)

toolbarFrame= tkinter.Frame(master=root)
toolbarFrame.grid(row=8,column=3,columnspan=5)

toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()
#canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

file_loaded = False
########################################################

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)

#------------------Quit The Window------------------------#

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

quit_button = tkinter.Button(master=root, text="Quit", command=_quit)

#-------------Read file and update param options---------------------#

choices = (' ')
var = tkinter.StringVar(root)
var.set('')
param_options = tkinter.OptionMenu(root,var,*choices)
def callback(*args):
    plot()
var.trace('w',callback)

log_header = []
log_df = pd.DataFrame(data={'x':[1,2,3],'y':[1,1,1]})

def read_log():
    global log_header
    global log_df
    global file_loaded
    file_loaded = True
    filename = askopenfilename()

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
    df_log['Step'] = df_log['Step']*0.000001

    log_header = header
    log_df = df_log
    var.set(header[0])
    param_options['menu'].delete(0,'end')
    for param in header:
        param_options['menu'].add_command(label=param, command=tkinter._setit(var,param))

file_button = tkinter.Button(master=root, text="Pick a File", command=read_log)

#------------------Plot the data----------------------#
    
def plot():
    global file_loaded
    if file_loaded:
        ax.cla()
        xdata = log_df['Step']
        ydata = log_df[var.get()]
        ax.plot(xdata,ydata)
        ax.set_title(var.get()+' vs. Step')
        ax.set_xlabel('Step')
        ax.set_ylabel(var.get())
        canvas.draw()

plot_button = tkinter.Button(root,text="Plot",command=plot)

#------------------------Span Selector---------------------#
def onselect(xmin, xmax):
    if file_loaded:
        plot()
        indmin, indmax = np.searchsorted(log_df['Step'], (xmin, xmax))
        indmax = min(len(log_df['Step']) - 1, indmax)

        thisx = log_df['Step'][indmin:indmax]
        thisy = log_df[var.get()][indmin:indmax]
        slope, intercept, r, p, std = linregress(thisx,thisy)
        print(slope)
        ax.plot(thisx,thisx*slope+intercept)
        #line2.set_data(thisx, thisy)
        #ax2.set_xlim(thisx[0], thisx[-1])
        #ax2.set_ylim(thisy.min(), thisy.max())
        fig.canvas.draw()

# Set useblit=True on most backends for enhanced performance.
span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'))
#-------------------Display Labels---------------------#

ave_label = tkinter.Label(root,text='Average:')
#slope_label = tkinter.Label(root,text='Slope:')

#----------------------Placements-----------------------#

plot_button.grid(row=6,column=5)
quit_button.grid(row=7,column=3)
param_options.grid(row=6,column=1)
file_button.grid(row=6,column=3)
ave_label.grid(row=6,column=2)
#slope_label.pack(side=tkinter.RIGHT)

#------------------------------------------------------#


            

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.