import networkx as nx


def compact_graph(g):
    new_graph = nx.DiGraph()
    for e in g.edges(data=True):
        coord0 = g.nodes[e[0]]["data"].coord
        coord1 = g.nodes[e[1]]["data"].coord
        new_graph.add_node(e[0], x=coord0.lon, y=coord0.lat)
        new_graph.add_node(e[1], x=coord1.lon, y=coord1.lat)
        new_graph.add_edge(
            e[0], e[1], data=e[2]["data"].edgeType.value.startswith("CONNECTION")
        )
    return new_graph
