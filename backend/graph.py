import igraph


def get_graph(filename):
    """

    Get graph by filename with extension graphml

    :param filename: str, absolute or relative f
    :return: igraph.Graph object
    """

    graph = igraph.Graph.Read_GraphML(filename)
    return graph


def save_graph(graph, filename):
    """

    save graph by filename with extension graphml

    :param graph: absolute or relative f
    :param filename: absolute or relative f
    """
    graph.write_graphml('static/' + filename)
