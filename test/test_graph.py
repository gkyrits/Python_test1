import matplotlib.pyplot as plt
import numpy as np
import threading as thrd
import time as tm

def test1():    
    # Sample data
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    # Create a plot
    plt.plot(x, y)
    # Add title and labels
    plt.title('Sample Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    # Show the plot
    plt.show()
    # Save the plot as an image
    #plt.savefig('sample_plot.png')      

def test2():
    fig, axs = plt.subplots(3)             # Create a figure containing a single Axes.
    axs[0].plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the Axes.
    axs[1].plot([5, 6, 7, 8], [1, 4, 2, 3])  # Plot some data on the Axes.   
    axs[2].plot([5, 6], [2, 3])  
    plt.show()                           # Show the figure.   


def test3():
    global ax
    fig, ax = plt.subplots()
    ax.axis([0, 10, 0, 10])
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3], label='alfa', color='r')  # Plot some data on the Axes.
    ax.plot([5, 6, 7, 8], [1, 4, 2, 3], label='bhta', color='b')  # Plot some data on the Axes.   
    ax.plot([5, 6], [2, 3], label='gama', color='g') 
    ax.text(2, 8, 'max=1 min=2')
    ax.grid(True)
    ax.legend()    
    plt.show()



def plot_change():
    global ax    
    tm.sleep(3)
    for art in ax.lines:    
        if art.get_label() == 'alfa':
            print("modify alfa ...")
            art.set_linewidth(5)
            art.set_linestyle('dotted')
            art.set_color('r')  
            ax.legend()
            plt.draw()            
    tm.sleep(3)
    for art in ax.lines:    
        if art.get_label() == 'bhta':
            print("modify bhta ...")
            art.remove()
            ax.legend()
            plt.draw()
    tm.sleep(3)
    for art in ax.lines:    
        if art.get_label() == 'gama':
            print("modify gama ...")            
            art.remove()
            ax.plot((5, 6, 7, 8), (1, 4, 2, 3), label='gama', color='g')
            ax.legend()            
            plt.draw()
    tm.sleep(3)
    for art in ax.lines:    
        if art.get_label() == 'gama':
            print("modify gama add ...")
            data = art.get_data()
            xd = list(data[0])
            yd = list(data[1])
            xd = np.append(xd,(1,2,3,4))
            yd = np.append(yd,(1,2,3,4))
            art.set_data(xd,yd)
            plt.draw()            


def test_plot_change():    
    print("Start")
    plt_thrd=thrd.Thread(target=plot_change)
    plt_thrd.start()
    test3()
    plt_thrd.join()
    print("End")



if __name__ == '__main__':
    test_plot_change()