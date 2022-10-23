import os
import sys
import numpy as np
import matplotlib.pyplot as plt

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
        plt.savefig(os.path.join(plot_folder_path, image_title))
        plt.close()


    #params desc: product_class_dfs = list[df per product class], classes = list of types of classes e.g. ["last 50%", 'mid 30%', 'top 20%'] 
    def plot_product_classes(self, dfs_product_class, classes):
        # source: https://www.geeksforgeeks.org/create-a-grouped-bar-plot-in-matplotlib/ 
        X_axis = np.arange(len(classes)) 

        for index, df in enumerate(dfs_product_class):
            x_class = X_axis[index]
            y_class = len(df)
            label_class = classes[index]
            plt.bar(x_class, y_class, 0.4, label=label_class)

        plt.xticks(X_axis, classes)
        plt.xlabel("Product classes")
        plt.ylabel("Number of products")
        plt.title("Number of products per product class")
        plt.legend()
        plt.savefig(os.path.join(plot_folder_path, "product_classes.png"))
        plt.close()

    def plot_total_profit_per_product_class(self, dfs_profits, classes):
        X_axis = np.arange(len(classes)) 

        for index, df in enumerate(dfs_profits):
            x_class = X_axis[index]
            y_class = sum(df)
            label_class = classes[index]
            plt.bar(x_class, y_class, 0.4, label=label_class)

        plt.xticks(X_axis, classes)
        plt.xlabel("Product classes")
        plt.ylabel("Profits")
        plt.title("Total profit per product class")
        plt.legend()
        plt.savefig(os.path.join(plot_folder_path, "total_profit_per_product_class.png"))
        plt.close()

