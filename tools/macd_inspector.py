'''Show macds results using matplotlib plots.'''
import json
import sys
import time
import matplotlib.pyplot as plt


def read_macds_file(macd_file):
    '''Read json file and return json converted into dict.'''
    with open(macd_file, 'r') as file:
        return json.load(file)


def main():
    '''Show interactive plot representing macd results'''
    plt.ion()
    fig = plt.figure()
    macd_graph = fig.add_subplot(111)
    macd_results = read_macds_file(sys.argv[1])[-200:]

    macds = []
    emamacds = []
    timeline = []
    for i, result in enumerate(macd_results):
        macds.append(result['macd'])
        emamacds.append(result['ema_macd_9'])
        timeline.append(i)

    line1, = macd_graph.plot(timeline, macds, 'b')
    line2, = macd_graph.plot(timeline, emamacds, 'r')

    while True:
        macd_results = read_macds_file(sys.argv[1])[-200:]

        macds = []
        emamacds = []
        timeline = []
        for i, result in enumerate(macd_results):
            macds.append(result['macd'])
            emamacds.append(result['ema_macd_9'])
            timeline.append(i)

        line1.set_ydata(macds)
        line1.set_xdata(timeline)
        line2.set_ydata(emamacds)
        line2.set_xdata(timeline)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(1)


if __name__ == '__main__':
    main()
