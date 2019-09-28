import igraph


def get_graph(filename):
    """

    Get graph by filename with extension graphml

    :param f: igraph.Graph object
    :param source: the source for the calculated paths
    :param target: the destination for the calculated paths. This can be a single vertex  ID, a list of vertex IDs, a
    single vertex name, a list of vertex names or a VertexSeq object. None means all the vertices
    :param weights: edge weights in a list or the name of an edge attribute holding edge weights. If None, all edges are
    assumed to have equal weight
    :param mode: the directionality of the paths. IN means to calculate incoming paths, OUT means to calculate outgoing
    paths, ALL means to calculate both ones.
    :param output: If this is "vpath", a list of vertex IDs will be returned, one path for each target vertex. For
    unconnected graphs, some of the list elements may be empty. Note that in case of mode=IN, the vertices in a path are
    returned in reversed order. If output="epath", edge IDs are returned instead of vertex IDs
    :return: list of edges or nodes on the path, e.g.
        - a call to get_shortest_paths(graph, 0, 1120, output="vpath") returns
            [[0, 16, 414, 408, 404, 670, 1081, 1070, 1071, 1114, 1116, 1119, 1120]]  #<-- vertex ids
        - a call to get_shortest_paths(graph, 0, 1120, output="epath") returns
            [[0, 30, 541, 523, 524, 867, 1360, 1357, 1364, 1423, 1427, 1430]]  #<-- edge ids
    """

    graph = igraph.Graph.Read_GraphML(filename)
    return graph


def save_graph(graph, filename):
    graph.write_graphml('static/' + filename)
