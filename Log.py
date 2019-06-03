
####################################################################

import tkinter
import numpy as np
import pandas as pd
from scipy.stats import linregress
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

################### Tkinter Set-up ######################
#    
root = tkinter.Tk()
root.wm_title("Log Analysis")

################### Figure Set-up ######################
#                   --------------
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)  
canvas.draw()
canvas.get_tk_widget().grid(row=0,column=3,sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

toolbarFrame= tkinter.Frame(master=root)
toolbarFrame.grid(row=8,column=3,columnspan=5)

toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()

################### Global Variables ######################
#   

file_loaded = False
line_plot = False
all_runs = {}
log_header = []
log_df = pd.DataFrame(data={'x':[1,2,3],'y':[1,1,1]})

################ Key Press for Some Reason #################
#  

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)

##################### Quit The Window ######################
#     

def _quit():
    root.quit()     
    root.destroy() 

quit_button = tkinter.Button(master=root, text="Quit", command=_quit)

################### Update run options ###################
#                  --------------------

run_choices = (' ')
run_var = tkinter.StringVar(root)
run_var.set('')
run_options = tkinter.OptionMenu(root,run_var,*run_choices)

def run_callback(*args):
    global all_runs
    curr_y_param = y_param_var.get()
    curr_x_param = x_param_var.get()
    header = list(all_runs[run_var.get()])

    if curr_y_param not in header:
        curr_y_param =  'Step'
    y_param_var.set(curr_y_param)
    y_param_options['menu'].delete(0,'end')
    for y_param in header:
        y_param_options['menu'].add_command(label=y_param, command=tkinter._setit(y_param_var,y_param))

    if curr_x_param not in header:
        curr_x_param =  'Step'
    x_param_var.set(curr_x_param)
    x_param_options['menu'].delete(0,'end')
    for x_param in header:
        x_param_options['menu'].add_command(label=x_param, command=tkinter._setit(x_param_var,x_param))

    plot()

run_var.trace('w',run_callback)

################### Update  x_param options ###################
#                  ----------------------

x_param_choices = (' ')
x_param_var = tkinter.StringVar(root)
x_param_var.set('')
x_param_options = tkinter.OptionMenu(root,x_param_var,*x_param_choices)

def callback(*args):
    plot()

x_param_var.trace('w',callback)

################### Update  y_param options ###################
#                  ----------------------

y_param_choices = (' ')
y_param_var = tkinter.StringVar(root)
y_param_var.set('')
y_param_options = tkinter.OptionMenu(root,y_param_var,*y_param_choices)
y_param_var.trace('w',callback)

################### Update plotting options ###################
#    

plot_choices = ('Line','Scatter','Histogram')
plot_var = tkinter.StringVar(root)
plot_var.set('Line')
plot_options = tkinter.OptionMenu(root,plot_var,*plot_choices)
plot_var.trace('w',callback)


######################## Read log file ########################
#                       ---------------

def read_log():
    global log_header
    global log_df
    global file_loaded
    global all_runs
    all_runs = {}
    file_loaded = True
    filename = askopenfilename()

    with open(filename) as log:
        logLines = [line.split() for line in log.readlines() if len(line.split()) != 0]
    run_number = 1
    thisRun = []
    start = False
    every = False
    for line in logLines:
        if line[0] == 'run':
            run = 'run'+str(run_number)
            if 'every' in line:
                every = True
                continue
            else:
                every = False
                continue
        if line[0] == 'Step':
            start = True
            header= line
            continue
        if line[0] == 'Loop':
            if not every:
                all_runs[run]=pd.DataFrame(data = np.asarray(thisRun).astype('float'), columns=header)
                run_number+=1
                thisRun = []
            start = False
            continue
        if start:
            thisRun.append(line)
    if run not in list(all_runs):
        all_runs[run]=pd.DataFrame(data = np.asarray(thisRun).astype('float'), columns=header)

    for run in list(all_runs):
        all_runs[run]['Step'] *= 0.000001
    run_var.set(list(all_runs)[0])
    run_options['menu'].delete(0,'end')
    for run in list(all_runs):
        run_options['menu'].add_command(label=run, command=tkinter._setit(run_var,run))

    header = list(all_runs[run_var.get()])
    y_param_var.set(header[0])
    y_param_options['menu'].delete(0,'end')
    for y_param in header:
        y_param_options['menu'].add_command(label=y_param, command=tkinter._setit(y_param_var,y_param))

    x_param_var.set(header[0])
    x_param_options['menu'].delete(0,'end')
    for x_param in header:
        x_param_options['menu'].add_command(label=x_param, command=tkinter._setit(x_param_var,x_param))

file_button = tkinter.Button(master=root, text="Pick a File", command=read_log)

#################### Plot the data ######################
#     
    
def plot():
    global file_loaded
    global line_plot
    global all_runs
    if file_loaded:
        ax.cla()
        xdata = all_runs[run_var.get()][x_param_var.get()]
        ydata = all_runs[run_var.get()][y_param_var.get()]
        if plot_var.get() == 'Line':
            ax.plot(xdata,ydata)
            ax.set_title(y_param_var.get()+' vs. '+ x_param_var.get())
            ax.set_xlabel(x_param_var.get())
            ax.set_ylabel(y_param_var.get())
            line_plot = True
        elif plot_var.get() == 'Scatter':
            ax.scatter(xdata,ydata)
            ax.set_title(y_param_var.get()+' vs. ' + x_param_var.get())
            ax.set_xlabel(x_param_var.get())
            ax.set_ylabel(y_param_var.get())
            line_plot = True
        else:
            ax.hist(ydata,bins = 100)
            line_plot = False
            ax.set_title(y_param_var.get())
            ax.set_xlabel(y_param_var.get())
            ax.set_ylabel('Freq')
        canvas.draw()

################### Span Selector ######################
#     

def onselect(xmin, xmax):
    global file_loaded
    global line_plot
    global all_runs
    if file_loaded and line_plot:
        plot()
        indmin, indmax = np.searchsorted(all_runs[run_var.get()][x_param_var.get()], (xmin, xmax))
        indmax = min(len(all_runs[run_var.get()][x_param_var.get()]) - 1, indmax)

        thisx = all_runs[run_var.get()][x_param_var.get()][indmin:indmax]
        thisy = all_runs[run_var.get()][y_param_var.get()][indmin:indmax]
        slope, intercept, r, p, std = linregress(thisx,thisy)
        print(slope)
        ax.plot(thisx,thisx*slope+intercept)
        fig.canvas.draw()


span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'))
#-------------------Display Labels---------------------#

#ave_label = tkinter.Label(root,text='Average:')
#slope_label = tkinter.Label(root,text='Slope:')

##################### Placements ########################
#   

plot_options.grid(row=6,column=5)
quit_button.grid(row=7,column=3)
y_param_options.grid(row=6,column=1)
x_param_options.grid(row=6,column=4)
file_button.grid(row=6,column=3)
run_options.grid(row=6,column=2)
#ave_label.grid(row=6,column=2)
#slope_label.pack(side=tkinter.RIGHT)

#------------------------------------------------------#


root.resizable(width=tkinter.TRUE, height=tkinter.TRUE)          

tkinter.mainloop()
