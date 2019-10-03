from collections import Iterable


def create_edges(graph, list_st_id):
    """

    Add edges to graph

    :param graph: igraph.Graph, graph to work on
    :param list_st_id: [(int,int)], list of (source vertex id - target vertex id) tuples
    :return: graph
    """
    graph.add_edges(list_st_id)

    return graph


def update_edge(graph, edge, **kwargs):
    """

    Edit a edge's attributes

    :param graph: igraph.Graph, graph to work on
    :param edge: igraph.Edge, edge to be updated
    :param kwargs: keyword arguments will be assigned as vertex attributes
    :return: graph
    """
    edge.update_attributes(**kwargs)

    return graph


def delete_edges(graph, edge):
    """

    Remove edges

    :param graph: igraph.Graph, graph to work on
    :param edge: igraph.Edge or igraph.EdgeSeq, edge(s) to be deleted
    :return: graph
    """
    if isinstance(edge, Iterable):
        graph.delete_vertices(edge)
    else:
        edge.delete()

    return graph
