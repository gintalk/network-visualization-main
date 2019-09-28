from collections import Iterable
from backend.utils import append_to_dictionary as append_to_dict


def read_edges(graph, list_edge_id=None):
    """

    Read edge data, this includes their attributes and each attribute's assigned value

    :param graph: igraph.Graph
    :param list_edge_id: [int], list of ids of edges to be retrieved; if None, retrieve all of them
    :return: dictionary of edges, e.g.
            {"0": {
                "this_attribute": "0",
                "that_attribute": "1"
                },
            "1": {
                "this_attribute": "2",
                "that_attribute": "3"
                }
            }
    """
    vertex_dict = {}
    vertices = graph.vs

    if list_edge_id is None:
        for vertex in vertices:
            append_to_dict(vertex_dict, vertex)
    else:
        for vertex_id in list_edge_id:
            append_to_dict(vertex_dict, vertices[vertex_id])

    return vertex_dict


def create_edges(graph, list_st_id):
    """

    Add edges to graph

    :param graph: igraph.Graph, graph to work on
    :param list_st_id: [(int,int)], list of (source vertex id - target vertex id) tuples
    :return:
    """
    graph.add_edges(list_st_id)

    return 0


def update_edge(edge, **kwargs):
    """

    Edit a edge's attributes

    :param edge: igraph.Edge, edge to be updated
    :param kwargs: keyword arguments will be assigned as vertex attributes
    :return:
    """
    edge.update_attributes(**kwargs)

    return 0


def delete_edges(edge):
    """

    Remove edges

    :param edge: igraph.Edge or igraph.EdgeSeq, edge(s) to be deleted
    :return:
    """
    if isinstance(edge, Iterable):
        edge[0].graph.delete_vertices(edge)
    else:
        edge.delete()

    return 0
