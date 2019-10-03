from collections import Iterable


def create_vertices(graph, n=None, name=None, **kwargs):
    """

    If n is present, add n vertices to graph. If name and kwargs are present, add one single vertex to graph

    :param graph: igraph.Graph, graph to work on
    :param n: int, number of vertices to add. If n is present, name and kwargs must be absent
    :param name: if a graph has C{name} as a vertex attribute, it allows one  to refer to vertices by their names in
    most places where igraph expects a vertex ID. If name is present, n must be absent
    :param kwargs: keyword arguments will be assigned as vertex attributes. If kwargs is present, n must be absent
    :return:
    """
    if name is None and not kwargs:
        graph.add_vertices(n)
    else:
        graph.add_vertex(name, **kwargs)

    return graph


def update_vertex(graph, vertex, **kwargs):
    """

    Edit a vertex's attributes

    :param graph: igraph.Graph, graph to work on
    :param vertex: igraph.Vertex, vertex to be updated
    :param kwargs: keyword arguments will be assigned as vertex attributes
    :return:
    """
    vertex.update_attributes(**kwargs)

    return graph


def delete_vertices(graph, vertex):
    """

    Remove vertices and their edges

    :param graph: igraph.Graph, graph to work on
    :param vertex: igraph.Vertex or igraph.VertexSeq, vertex or vertices to be deleted
    :return:
    """
    if isinstance(vertex, Iterable):
        graph.delete_vertices(vertex)
    else:
        vertex.delete()

    return graph
