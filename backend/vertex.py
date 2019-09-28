from collections import Iterable
from json import dumps
from backend.utils import append_to_dictionary as append_to_dict


def read_vertices(graph, list_vertex_id=None):
    """

    Read vertex data, this includes their attributes and each attribute's assigned value

    :param graph: igraph.Graph object
    :param list_vertex_id: list of ids of vertices to be retrieved; if None, retrieve all of them
    :return: jsonified dictionary of vertices, e.g.
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

    if list_vertex_id is None:
        for vertex in vertices:
            append_to_dict(vertex_dict, vertex)
    else:
        for vertex_id in list_vertex_id:
            append_to_dict(vertex_dict, vertices[vertex_id])

    return dumps(vertex_dict)


def create_vertices(graph, n=None, name=None, **kwargs):
    """

    If n is present, add n vertices to graph. If name and kwargs are present, add one single vertex to graph

    :param graph: igraph.Graph object
    :param n: number of vertices to add. If n is present, name and kwargs must be absent
    :param name: if a graph has C{name} as a vertex attribute, it allows one  to refer to vertices by their names in
    most places where igraph expects a vertex ID. If name is present, n must be absent
    :param kwargs: keyword arguments will be assigned as vertex attributes. If kwargs is present, n must be absent
    :return:
    """
    if name is None and not kwargs:
        graph.add_vertices(n)
        return 0

    graph.add_vertex(name, **kwargs)
    return 0


def update_vertex(vertex, **kwargs):
    """

    Edit a vertex's attributes

    :param vertex: igraph.Vertex object
    :param kwargs: keyword arguments will be assigned as vertex attributes
    :return:
    """
    vertex.update_attributes(**kwargs)
    return 0


def delete_vertices(vertex):
    """

    Remove vertices and their edges

    :param vertex: igraph.Vertex object or igraph.VertexSeq object
    :return:
    """
    if isinstance(vertex, Iterable):
        vertex[0].graph.delete_vertices(vertex)
    else:
        vertex.delete()

    return 0
