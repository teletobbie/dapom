import os
import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

plot_folder_path = os.path.join(sys.path[0], "plots")

class Graphs:
    def __init__(self):
        if os.path.isdir(plot_folder_path) == False:
            os.makedirs(plot_folder_path)


    def plot_error_bar(self, x_array, y_array, error_array, xlabel, ylabel, plot_title, image_title, ecolor=None):
        x = np.arange(0, len(x_array), 1)
        y = y_array
        error = error_array

        ax = plt.subplot()
        ax.errorbar(x, y, yerr=error, ecolor=ecolor)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(plot_title)

        plt.savefig(os.path.join(plot_folder_path, image_title))
        plt.close()

    def plot_hist(self, x_array, xlabel, ylabel, plot_title, image_title, bins=None):
        # TODO: set three classes of products based on the average daily profit (is this correct?)
        ax_hist = plt.subplot()
        ax_hist.hist(x_array, bins=bins)
        ax_hist.set_xlabel(xlabel)
        ax_hist.set_ylabel(ylabel)
        ax_hist.set_title(plot_title)
        # plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.savefig(os.path.join(plot_folder_path, image_title))
        plt.close()
        # plt.show()
