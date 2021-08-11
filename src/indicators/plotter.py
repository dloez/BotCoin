'''Plotting indicators data.'''
import warnings
from multiprocessing import Process
import matplotlib.pyplot as plt


class Plotter(Process):
    '''Shows indicators data using matplotlib plots.'''
    def __init__(self, queue, idx):
        Process.__init__(self)
        warnings.filterwarnings('ignore')

        self.queue = queue
        self.idx = idx

        self._figure = None
        self._ax = None

        self._data = []
        self._functions = []

    def run(self):
        plt.ion()
        self._figure = plt.figure()
        self._ax = self._figure.add_subplot(111)

        lines = []
        for function in self._functions:
            lines.append(self._ax.plot((), (), f"{function['color']}{function['type']}")[0])

        while True:
            data = self.queue.get()
            self._process_data(data)
            for i, line in enumerate(lines):
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

    def _process_data(self, data):
        if len(data) == 100:
            self._data = [[list(range(0, 100))]]
            for _ in range(len(data[0])):
                self._data.append([])

            for dataset in data:
                for i, value in enumerate(dataset):
                    self._data[i + 1].append(value)
        else:
            for dataset in data:
                for i, value in enumerate(dataset):
                    self._data[i + 1].append(value)
                    self._data[i + 1] = self._data[i + 1][-100:]
