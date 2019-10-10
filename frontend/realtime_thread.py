from threading import Thread
from time import sleep

from numpy import random

class RealTimeMode():

    def __init__(self, parent):
        self.vertexAttr = None
        self.edgeAttr = None
        self.fps = 30
        self.realtimeState = None
        self.thread = None
        self.parent = parent

    def set(self):
        self.realtimeState = True
        self.thread = Thread(target=self.doRealTime, daemon=True)
        self.thread.start()

    def unset(self):
        self.realtimeState = False
        self.thread.join()

    def doRealTime(self):
        g = self.parent.graph
        print("Do real time " ,self.vertexAttr)
        while self.realtimeState:
            if len(self.vertexAttr) > 0:
                for v in self.vertexAttr:
                    if v[0] == "Normal Distribution":
                        g.vs[v[2]] = [abs(random.normal(i, v[1])) for i in g.vs[v[2]]]
                    else:
                        g.vs[v[2]] = [abs(random.uniform(i - v[1], i + v[1])) for i in g.vs[v[2]]]

            if len(self.edgeAttr) > 0:
                for edge in self.edgeAttr:
                    if edge[0] == "Normal Distribution":
                        g.es[edge[2]] = [abs(random.normal(i, edge[1])) for i in g.es[edge[2]]]
                    else:
                        g.es[edge[2]] = [abs(random.uniform(i - edge[1], i + edge[1])) for i in g.es[edge[2]]]

            self.canvas.notifyGraphUpdated()
            self.canvas.update()
            sleep(1.0 / self.fps)
