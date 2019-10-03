def __init__(self, parent):
    super().__init__()
    self.parent = parent

    self.graph_to_display = None
    self.clustering_algorithm = None
    self.graph_center = None
    self.scale_factor = None
    self.points = []
    self.lines = []

    self.init_variables()


def init_variables(self):
    self.graph_to_display = self.parent.main_window.graph
    self.clustering_algorithm = self.parent.main_window.clustering_algorithm

    graph_rect = QRect(
        QPoint(min(self.graph_to_display.vs['x']), min(self.graph_to_display.vs['y'])),
        QPoint(max(self.graph_to_display.vs['x']), max(self.graph_to_display.vs['y']))
    )
    self.graph_center = QPoint(graph_rect.center())
    self.scale_factor = scale_factor_hint(self.parent.geometry(), graph_rect, 1.1)


def assign_vertex_to_cluster():
    for v in self.graph_to_display.vs:
        for cluster in clusters:
            if v['id'] in cluster.vs['id']:
                v['color'] = cluster.color
                break


colors = [
                (255, 255, 255), (255, 0, 0), (255, 128, 0), (255, 255, 0),     # white, red, orange, yellow
                (128, 255, 0), (160, 160, 160), (0, 255, 255), (0, 128, 255),   # green, gray, light blue, medium blue
                (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128),       # blue, purple, pink, burgundy
                (0, 0, 0)                                                       # black
            ]
