'''Plotting indicators data.'''
import warnings
import threading
import matplotlib.pyplot as plt


class Plotter(threading.Thread):
    '''Shows indicators data using matplotlib plots.'''
    def __init__(self):
        threading.Thread.__init__(self)
        warnings.filterwarnings('ignore')

        self._figure = None
        self._ax = None

        self._functions = []
        self._data = [[]]
        self._lines = []

    def run(self):
        plt.ion()
        self._figure = plt.figure()
        self._ax = self._figure.add_subplot(111)

        for function in self._functions:
            self._data.append([])
            self._lines.append(self._ax.plot((), (), f"{function['color']}{function['type']}")[0])

        while True:
            for i, line in enumerate(self._lines):
                line.set_xdata(self._data[0])
                line.set_ydata(self._data[i + 1])
                self._ax.relim()
                self._ax.autoscale_view(True,True,True)
                self._figure.canvas.draw()
                self._figure.canvas.flush_events()

    def setup_plot(self, functions):
        '''Add functions to plot.'''
        self._functions = functions
        self.start()

    def add_data(self, data):
        '''Add data to plot.'''
        if len(self._data[0]) != 0:
            self._data[0].append(self._data[0][-1] + 1)
            self._data[0] = self._data[0][-100:]
        else:
            self._data[0].append(0)

        for i, value in enumerate(data):
            self._data.append([])
            self._data[i + 1].append(value)
            self._data[i + 1] = self._data[i + 1][-100:]
