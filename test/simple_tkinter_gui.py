import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mplt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  NavigationToolbar2Tk) 


def plot(): 
  
    # the figure that will contain the plot 
    fig = mplt.figure.Figure(figsize = (5, 5), 
                 dpi = 100) 
  
    # data
    x = np.linspace(0,2*np.pi,100)    
    y = np.sin(x)

    # adding the subplot 
    plot1 = fig.add_subplot(111) 
  
    # plotting the graph 
    plot1.plot(y) 
  
    # creating the Tkinter canvas 
    # containing the Matplotlib figure 
    canvas = FigureCanvasTkAgg(fig, master = window)   
    canvas.draw() 
  
    # placing the canvas on the Tkinter window 
    canvas.get_tk_widget().grid()
  
    # creating the Matplotlib toolbar 
    toolbar = NavigationToolbar2Tk(canvas, window) 
    toolbar.update() 
  
    # placing the toolbar on the Tkinter window 
    canvas.get_tk_widget().grid()
    
def PeakBack():
    return 0

def PeakForward():
    return 0

def SaveEntry():
    return 0

if __name__ == '__main__':

    window = tk.Tk()
    window.title('test window')

    buttons = tk.LabelFrame(window, text='Controls', padx=5, pady=5).grid(row=0, column=1, sticky=tk.E + tk.N + tk.S)
    plots = tk.LabelFrame(window, text='Plots', padx=5, pady=5).grid(row=0, column=0, sticky=tk.W + tk.N + tk.S + tk.E)

    plots_button = tk.Button(plots, text='plot', command=plot).grid(row=0, column=0, sticky=tk.W + tk.N + tk.S + tk.E)

    peak_label = tk.Label(buttons, text='Change Current Peak').grid(row=0, column=0, sticky=tk.E)
    peak_button_back = tk.Button(buttons, text='<', command=PeakBack).grid(row=1, column=0, sticky=tk.E)
    peak_button_forward = tk.Button(buttons, text='>', command=PeakForward).grid(row=1, column=1, sticky=tk.E)

    beacon_choice = tk.IntVar()
    beacons_label = tk.Label(buttons, text='Beacon Label').grid(row=2, column=0, sticky=tk.E)
    beacon_0 = tk.Radiobutton(buttons, text='3008', variable=beacon_choice, value=0).grid(row=3, column=0, sticky=tk.E)
    beacon_1 = tk.Radiobutton(buttons, text='2407', variable=beacon_choice, value=1).grid(row=3, column=1, sticky=tk.E)
    beacon_2 = tk.Radiobutton(buttons, text='2408', variable=beacon_choice, value=2).grid(row=3, column=2, sticky=tk.E)    

    pulse_status = tk.IntVar()
    pulse_label = tk.Label(buttons, text='True Peak?').grid(row=4, column=0, sticky=tk.E)
    pulse_true = tk.Radiobutton(buttons, text='Yes', variable=pulse_status, value=1).grid(row=5, column=0, sticky=tk.E)
    pulse_false = tk.Radiobutton(buttons, text='No', variable=pulse_status, value=0).grid(row=5, column=1, sticky=tk.E)    

    save_entry_button = tk.Button(buttons, text='Save Entry', command=SaveEntry).grid(row=6, column=0, sticky=tk.E)
    
    #entry_1 = tk.Entry(window).grid(row=0, column=1, sticky=tk.W+tk.E)
    #entry_2 = tk.Entry(window).grid(row=1, column=1, sticky=tk.W+tk.E)
    
    window.columnconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)

    window.mainloop()


        
