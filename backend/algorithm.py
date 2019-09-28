from igraph import InternalError


def get_shortest_paths(graph, source, target=None, weights=None, mode="OUT", output="vpath"):
    """

    Calculates the shortest paths from/to a given node in a graph.

    :param graph: igraph.Graph, graph to work on
    :param source: int, the source for the calculated paths
    :param target: int, the destination for the calculated paths. This can be a single vertex  ID, a list of vertex IDs,
    a single vertex name, a list of vertex names or a VertexSeq object. None means all the vertices
    :param weights: str or [int or float], edge weights in a list or the name of an edge attribute holding edge weights.
    If None, all edges are assumed to have equal weight
    :param mode: str, the directionality of the paths. IN means to calculate incoming paths, OUT means to calculate
    outgoing paths, ALL means to calculate both ones.
    :param output: str, If this is "vpath", a list of vertex IDs will be returned, one path for each target vertex. For
    unconnected graphs, some of the list elements may be empty. Note that in case of mode=IN, the vertices in a path are
    returned in reversed order. If output="epath", edge IDs are returned instead of vertex IDs
    :return: [[int]], list of edges or nodes on the path, e.g.
        - a call to get_shortest_paths(graph, 0, 1120, output="vpath") returns
            [[0, 16, 414, 408, 404, 670, 1081, 1070, 1071, 1114, 1116, 1119, 1120]]  #<-- vertex ids
        - a call to get_shortest_paths(graph, 0, 1120, output="epath") returns
            [[0, 30, 541, 523, 524, 867, 1360, 1357, 1364, 1423, 1427, 1430]]  #<-- edge ids
    """
    return graph.get_shortest_paths(source, target, weights, mode, output)


def bottleneck(graph, source, target, capacity=None, output="e"):
    """
    Find bottleneck of graph

    :param graph: igraph.Graph, graph to work on
    :param source: int, the source vertex id
    :param target: int, the target vertex id
    :param capacity: [str] or None, the capacity of the edges. It must be a list or a valid attribute name or None. In
    the latter case, every edge will have the same capacity
    :param output: ignore this for now
    :return: [int], list of ids of edges that cause the bottleneck between two vertices
    """
    cut = graph.maxflow(source, target, capacity)

    if output == "v":
        partition_list = [cut[0], cut[1]]
        return partition_list

    if output == "e":
        bottleneck_edge = []
        for vt_a_id in cut[0]:
            for vt_b_id in cut[1]:
                vt_a = graph.vs[vt_a_id]
                vt_b = graph.vs[vt_b_id]
                try:
                    edge_id = graph.get_eid(vt_a.index, vt_b.index)
                except InternalError:
                    continue
                bottleneck_edge.append(edge_id)

        return bottleneck_edge
