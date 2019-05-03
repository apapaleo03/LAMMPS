import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from os import listdir,mkdir
import re

################################################################


def delta_length(dir,timestep,div):
    """
    Plot the change in length with respect to time
    :param dir: directory of the files
    :param timestep: timestep of the simulation
    :param div: determine the number of chunks for find_linear_portion()
    :return: return a file and array containing the growth velocities
    """
    plt.figure(figsize=(20, 10))
    files = sorted(listdir(dir))
    orientation,temp = [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', files[0])]
    orientation = str(int(orientation))
    title = '[' + orientation + '] Length vs Time'
    slopes = []

    for file in files:
        temp = get_temp(file)
        step, lz = np.loadtxt(dir + file, float, unpack=True)
        step = step * timestep * timestep
        min, max = find_linear_portion2(step,lz,div)
        slope, intcpt, r, p, std_srr = linregress(step[min:max], lz[min:max])
        slopes.append([-1 * slope,temp])

        plt.plot(step, lz, label= str(temp)+'[K]')
        #poly_params = np.polyfit(step, lz, 3)
        #poly_3 = np.poly1d(poly_params)
        #yPoly = poly_3(step)
        #plt.plot(step, lz, 'o')#, step, yPoly, '-')
        plt.plot(step,step*slope+intcpt)

    plt.xlabel('Time [ns]')
    plt.ylabel('Length [A]')
    plt.title(title)
    plt.grid()
    plt.legend()
    plt.savefig(title)
    plt.show()

    #write_slope_data(orientation,slopes)


################################################################

def get_temp(file):
    """
    Returns the temperature of the file
    :param file: the file of which the temperature will be obtained
    :return: temperature
    """
    specs = [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', file)]
    return specs[-1]

################################################################

def find_linear_portion(step,lz,div):
    """
    Compared the slopes of chunks of the data to determine the end of the linear portion
    and returns the index
    :param step: steps
    :param lz: lengths
    :param div: number of chunks
    :return: min, max
    """
    max = -1
    min = 0
    prev = 0.1
    step_len = len(step)
    interval = int(step_len/div)
    found_start = False
    for i in range(step_len):

        if i % interval == 0:
            tr_step = step[i:i + interval]
            tr_lz = lz[i:i + interval]
            slope, intc, r, p, std = linregress(tr_step, tr_lz)
            if not found_start:
                if slope < 0:
                    min = i-interval
                    found_start = True
            if abs(slope / prev) < 0.3 and i > 500:
                max = i - interval


            prev = slope

    return min, max

################################################################

def write_slope_data(orientation,slopes):
    """
    Writes the data in the slopes parameter to a file
    :param orientation: orientation of the system
    :param slopes: array containing the slopes obtained from linregress
    :return:
    """

    with open(str(int(orientation)) + '_slopes.txt', 'w') as fil:
        fil.write("# " + str(int(orientation))+'\n')

        for dat in slopes:
            fil.write(str(dat[0]) + ' ' + str(dat[1])+'\n')

################################################################

def delta_velocity(slope_files=[], slope_arrays=[]):
    """
    Plots the velocity vs temperature
    :param slope_files: an array of the data files
    :param slope_arrays: an array of the data arrays
    :return:
    """
    plt.figure(figsize=(20, 10))

    if slope_files:

        for data in slope_files:

            with open(data) as file:
                orientation = file.readline().split()[1]

            slopes, temps = np.loadtxt(data, float, unpack=True)
            plt.plot(temps, slopes, 'o', label=orientation)

    plt.axhline(0)
    plt.title('Growth vs. Temperature')
    plt.xlabel('Tempaerature [K]')
    plt.ylabel('Velocity [A/ns]')
    plt.legend()
    plt.grid()
    plt.savefig('GrowthvTemp')
    plt.show()

################################################################


def test_slope(slope,div = 10):
    """
    Determine how to locate the end of the linear portion of a slope.
    Finds the slope of evenly spaced chunks determined by the length of the array
        divided by div
    compares the slopes of chunks and returns when the linear portion is found
    :param slope: the slope to be analyzed
    :param div: divides the slope into 'div' sized chunks
    :return:
    """
    plt.figure(figsize=(20,10))
    step, lz = np.loadtxt(slope, float, unpack = True)
    step_len = len(step)
    print(step_len)
    plt.plot(step,lz)
    inv = int(step_len/div)
    max = -1
    min = 0
    prev = 0.1
    found_start = False
    for i in range(len(step)):

        if i%inv == 0:
            tr_step = step[i:i+inv]
            tr_lz = lz[i:i+inv]
            slope, intc, r, p, err = linregress(tr_step, tr_lz)
            plt.plot(tr_step,tr_step*slope + intc)
            if not found_start:
                if slope < 0:
                    min = i - inv
                    found_start = True

            if abs(slope/prev) < 0.3 and i > 500:
                plt.text(tr_step[-1],tr_lz[-1],slope/prev)
                print(step[i],i)
                max = i - inv
                #break

            prev = slope
    print(max)
    print(min)

    slope, intcpt, r, p, std_srr = linregress(step[min:max], lz[min:max])
    plt.plot(step[min:max], step[min:max] * slope + intcpt)

    plt.show()


################################################################


def clean(dir,span = 400):
    """
        Takes noisy data and refines it by taking the average at equal intervals and creates
        a new array based on those averages.

        The average lengths and step are output to a file for each temperature and the files
        are then put into a directory 'Cleaned_Lengths'.

        If the directory does not exist, it is created.

        :param dir: location of the files to be cleaned
        :param intervals: dictates how often the averages should be taken
    """
    files = listdir(dir)
    path = 'Cleaned_Lengths'
    print(listdir('.'))

    if path not in listdir('.'):

        try:  
            mkdir(path)
        except OSError:  
            print ("Creation of the directory %s failed" % path)
        else:  
            print ("Successfully created the directory %s " % path)

    for file in files:
        step, lz = np.loadtxt(dir+file, float, unpack = True)
        step_len = len(step)
        run_lz = []
        run_step = step
        for i in range(step_len):
            cur_ave = 0
            if i < span:
                cur_ave = np.average(lz[(i + (-1 * i)):(i + span)])
            elif i >= span:
                if i + span > step_len:
                    cur_ave = np.average(lz[(i + (-1 * span)):(i + (step_len - i))])
                else:
                    cur_ave = np.average(lz[(i + (-1 * span)):(i + span)])
            try:
                run_lz.append(cur_ave)
            except:
                print(i)

        with open(path+'/'+file,'w') as data:

            for i in range(len(run_lz)):
                data.write(str(run_step[i]) + ' ' + str(run_lz[i]) + '\n')


        

################################################################


def test_slope2(slope,div = 20,pol=3):

    #plt.figure(figsize=(20,10))
    step, lz = np.loadtxt(slope, float, unpack = True)
    step = step*0.000001
    step_len = len(step)
    plt.plot(step,lz)
    poly_params = np.polyfit(step, lz, pol)
    poly_3 = np.poly1d(poly_params)
    yPoly = poly_3(step)
    plt.plot(step,yPoly)
    inv = int(step_len/div)
    max = -1
    min = 0
    encountered_inflections = False
    slope, intc, r, p, err = linregress(step[0:inv], yPoly[0:inv])
    prev = slope
    found_start = False
    for i in range(len(step)):

        if i%inv == 0:
            tr_step = step[i:i+inv]
            tr_lz = yPoly[i:i+inv]
            slope, intc, r, p, err = linregress(tr_step, tr_lz)
            plt.plot(tr_step,tr_step*slope + intc)
            print (slope, slope/prev)
            if abs(slope/prev) < 0.4 and i > 300:
                plt.plot(step[i],lz[i],'o')
                if not encountered_inflections:
                    max = i
                else:
                    min = max
                    max = i
                encountered_inflections = True

            prev = slope
    if 1:
        slope1, intcpt1, r, p, std_srr = linregress(step[min:max], yPoly[min:max])
        slope2, intcpt2, r, p, std_srr = linregress(step[min:max], lz[min:max])
        plt.plot(step[min:max], step[min:max] * slope1 + intcpt1)
        plt.plot(step[min:max], step[min:max] * slope2 + intcpt2,':')

    plt.show()


def find_linear_portion2(step,lz,div):
    step_len = len(step)
    poly_params = np.polyfit(step, lz, 3)
    poly_3 = np.poly1d(poly_params)
    yPoly = poly_3(step)
    inv = int(step_len/div)
    max = -1
    min = 0
    encountered_inflections = False
    slope, intc, r, p, err = linregress(step[0:inv], yPoly[0:inv])
    prev = slope
    for i in range(len(step)):

        if i%inv == 0:
            tr_step = step[i:i+inv]
            tr_lz = yPoly[i:i+inv]
            slope, intc, r, p, err = linregress(tr_step, tr_lz)
            if abs(slope/prev) < 0.4 and i > 300:
                if not encountered_inflections:
                    max = i
                else:
                    min = max
                    max = i
                encountered_inflections = True

            prev = slope

    return min, max



    


