from threading import Thread
from time import sleep
import numpy as np
from PyQt5.QtGui import QPen, QColor
from sklearn.preprocessing import MinMaxScaler
import time

from numpy import random

class RealTimeMode():

    def __init__(self, parent):
        self.vertexAttr = None
        self.edgeAttr = None
        self.fps = 30
        self.realtimeState = None
        self.thread = None
        self.parent = parent
        self.scaler = MinMaxScaler()

    def set(self):
        self.realtimeState = True
        self.thread = Thread(target=self.doRealTime, daemon=True)
        self.thread.start()

    def unset(self):
        self.realtimeState = False
        self.thread.join()

    def doRealTime(self):
        graph = self.parent.graph
        initial_value = np.random.standard_normal(graph.ecount())
        while self.realtimeState:
            scaled_value = (np.sin(initial_value + time.time()) + 1) / 2.
            for line in self.parent.view.scene.lines:

                # line_pen = QPen(QColor(255 - bandwidth[n] * 255, 0, bandwidth[n] * 255))
                # line_pen.setWidthF(line.edge['edge_width'])
                # line.setPen(line_pen)
            self.view.update_view()
            sleep(1.0 / self.fps)
