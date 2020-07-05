def get_nodes_list(tuples):
    """From a list of tuples of edges returns the ordered list of nodes"""
    nodes = [list(t) for t in tuples]

    def reorder(nodes):

        if len(nodes) <= 1:
            return nodes

        for j in range(len(nodes) - 1):
            remaining = nodes[j:]
            first = remaining[0]
            for i in range(1, len(remaining)):
                chunk_1 = remaining[1:i]
                chunk_2 = remaining[i + 1 :]
                if first[-1] == remaining[i][0]:
                    return nodes[:j] + reorder(
                        chunk_1 + [first + remaining[i][1:]] + chunk_2
                    )
                if first[0] == remaining[i][-1]:
                    return nodes[:j] + reorder(
                        chunk_1 + [remaining[i] + first[1:]] + chunk_2
                    )
        return nodes

    ans = reorder(nodes)
    return ans


def find_common_node(nodes_1, nodes_2):
    for node in nodes_1:
        if node in nodes_2:
            return node
    return None


def get_adjacent_node(nodes, via_node):

    if via_node not in nodes:
        return None

    index = nodes.index(via_node)

    if index == 0:
        return nodes[index + 1]
    elif index == len(nodes) - 1:
        return nodes[index - 1]
    else:
        # TODO: Handle case when node is not start or end of way
        return None


def sort_nodes(current_nodes, new_nodes):
    joined_nodes = current_nodes[:]
    joined_nodes.extend(new_nodes)
    seen = set()
    return tuple(
        (node for node in joined_nodes if not (node in seen or seen.add(node)))
    )
