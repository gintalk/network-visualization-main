import matplotlib
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


class DataBar(FigureCanvas):

    def __init__(self, data, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.data = data

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot_data_count()

        self.show()

    def set_data(self, data):
        self.data = data

    def plot_data_count(self):
        data = self.data

        value = list(set(data))
        value = [str(x) for x in value]
        height = [data.count(x) for x in set(data)]

        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        ax.bar(value, height)
        for i in range(len(value)):  # your number of bars
            plt.text(x=i,  # takes your x values as horizontal positioning argument
                     y=height[i] + 1,  # takes your y values as vertical positioning argument
                     s=height[i],  # the labels you want to add to the data
                     size=9)

        ax.set_xticks(value)
        ax.set_xticklabels(value, rotation=-90)

    def clear_figure(self):
        self.axes.set_axis_off()
        self.update_figure()

    def update_figure(self):
        self.draw()
