from igraph import Edge


def append_to_dictionary(dictionary, item):
    """

        Make an entry in a dictionary for a given item

        :param dictionary: dict, dictionary of edge_id-(attribute-value)
        :param item: igraph.Edge or igraph.Vertex, vertex or edge to work on
        :return:
    """
    index = str(item.index)
    list_attribute = item.attributes()

    dictionary[index] = {}
    if isinstance(item, Edge):
        dictionary[index]["source"] = str(item.source)
        dictionary[index]["target"] = str(item.target)

    for attr in list_attribute:
        dictionary[index][attr] = str(item[attr])