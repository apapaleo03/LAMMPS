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
#######################################################
root = tkinter.Tk()
root.wm_title("Log Analysis")
#######################################################
fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
ax = fig.add_subplot(111)
ax.plot(t, 2 * np.sin(2 * np.pi * t))
#######################################################

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

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

log_header = []
log_df = pd.DataFrame(data={'x':[1,2,3],'y':[1,1,1]})

def read_log():
    global log_header
    global log_df
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
    ax.cla()
    xdata = log_df['Step']
    ydata = log_df[var.get()]
    #l.set_xdata(xdata)
    #l.set_ydata(ydata)
    #ax.set_xlim(min(xdata)-0.05*abs(max(xdata)),max(xdata)+0.05*max(xdata))
    #ax.set_ylim(min(ydata)-0.1*abs(min(ydata)),max(ydata)+0.1*max(ydata))
    ax.plot(xdata,ydata)
    canvas.draw()

plot_button = tkinter.Button(root,text="Plot",command=plot)

#--------------------Pick slope points------------------#

def pick():
    p1 = 0
    p2 = 0
    print('enter func')
 
    pts = np.asarray(fig.ginput(2, timeout=-1))
    p1 = pts[0][0]
    p2 = pts[1][0]
    print(p1,p2)
    found_p1 = False
    for i in range(len(log_df['Step'])):
        if log_df['Step'][i] > p1 and not found_p1:
            mini = i
            found_p1 = True

        if log_df['Step'][i] > p2:
            maxi = i  
            break   
    print(mini,maxi)
    slope, intercept, r, p, std = linregress(log_df['Step'][mini:maxi],
                                                 log_df[var.get()][mini:maxi])
    ax.plot(log_df['Step'][mini:maxi],
            log_df['Step'][mini:maxi]*slope+intercept, 'r')

    

pick_button = tkinter.Button(root,text="Pick SLope",command=pick)

#-------------------Display Labels---------------------#
ave_label = tkinter.Label(root,text='Average:')
slope_label = tkinter.Label(root,text='Slope:')

#----------------------Placements-----------------------#

plot_button.pack(side=tkinter.RIGHT )
quit_button.pack(side=tkinter.BOTTOM)
param_options.pack(side=tkinter.LEFT)
file_button.pack(side=tkinter.BOTTOM)
ave_label.pack(side=tkinter.LEFT)
slope_label.pack(side=tkinter.RIGHT)
pick_button.pack(side=tkinter.BOTTOM)

#------------------------------------------------------#


            

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.