from json import dumps


def get_vertices(graph, list_vertex_id=None):
    """
    returns a jsonified dictionary of vertices and their attribute-value pairs
    :param graph: igraph.Graph object
    :param list_vertex_id: list of ids of vertices to be retrieved; if None, retrieve all of them
    :return: jsonified dictionary of vertices
    """
    vertex_dict = vertex_dictify(list_vertex_id)

    return dumps(vertex_dict)


def add_vertices():
    #   args = {
    #      "vertices": int
    #   }

    args = request.json
    vertex_count = args["vertices"]

    graph_as_input.add_vertices(vertex_count)

    response = {"action": "Create", "code": "Success"}
    return make_response(jsonify(response), 201)


def edit_vertex():  # for now, can only edit one vertex at a time
    #    args = {
    #       "vertex": int,
    #       "attribute_name": string,
    #       "new_value": string or int
    #    }

    args = request.json
    vertex_id = args["vertex"]
    attr = args["attribute_name"]
    new_value = args["new_value"]

    vertex = graph_as_input.vs[vertex_id]
    vertex[attr] = new_value

    response = {"action": "Edit", "code": "Success"}
    return make_response(jsonify(response), 201)


def delete_vertices():
    #    args = {
    #       "attribute_name": string,
    #       "value": string or int
    #    }

    args = request.json
    attr = args["attribute_name"]
    value = args["value"]

    if attr == "index":
        vertex_list = value
        edge_list = [edge.index for edge in graph_as_input.es if edge.source == value or edge.target == value]
    else:
        vertex_list = [vertex.index for vertex in graph_as_input.vs if vertex[attr] == value]
        edge_list = [edge.index for edge in graph_as_input.es if edge.source in vertex_list
                     or edge.target in vertex_list]

    graph_as_input.delete_vertices(vertex_list)
    graph_as_input.delete_edges(edge_list)

    return str(graph_as_input)


""" Auxiliary functions """


def vertex_dictify(vertex_list):
    vertex_dict = {}
    attributes = graph_as_input.vs.attributes()

    if len(vertex_list) == 0:
        vertex_list = graph_as_input.vs

    for vertex_id in vertex_list:
        if isinstance(vertex_id, Vertex):
            vertex = vertex_id
        else:
            vertex = graph_as_input.vs[vertex_id]
        append_vertex_to_dictionary(vertex_dict, attributes, vertex)

    return vertex_dict


def append_vertex_to_dictionary(dictionary, attributes, vertex):
    index = str(vertex.index)

    dictionary[index] = {}

    for attr in attributes:
        dictionary[index][attr] = str(vertex[attr])
