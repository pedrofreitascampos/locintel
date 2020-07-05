"""
Scenarios for ODD generation/restriction of a base graph.

Steps to create scenarios:
1. Define your reference graph:
    Add/choose graph fixture
    -> This is your base/reference graph, analogous to our OSM base map

2. Define your final odd graph (expected output)
    Restrict base graph using/adding `restriction` functions
    -> This will create an ODD subgraph, which is the final result expected by the method under test

3. Generate synthetic scenarios
    Use/add `transformation` functions
   -> This will create synthetic inputs to the methods under test

4. Make sure these are fed to `generate_scenarios`
"""

from copy import deepcopy

import networkx as nx

from das.routing.graphs.datamodel.jurbey import Node

from allpairspy import AllPairs

from tests.synthetic.graphs import (
    urban_grid_no_geometry,
    urban_grid_node_geometry,
    urban_grid_node_and_edge_geometry,
)
from tests.synthetic.utils import (
    interpolated_geometry,
    create_edge,
    requires,
    find_midpoint,
)


########################################################
#                 ODD restrictions                     #
#                                                      #
#  Restriction to apply to base graph, to generate     #
#  synthetic ODDs                                      #
#                                                      #
########################################################
def no_restrictions(base_graph):
    odd_graph = deepcopy(base_graph)
    return odd_graph


def remove_node(base_graph):
    odd_graph = deepcopy(base_graph)
    odd_graph.remove_node(5)
    return odd_graph


def remove_edge(base_graph):
    odd_graph = deepcopy(base_graph)
    odd_graph.remove_edge(13, 5)
    return odd_graph


########################################################
#              Graph transformations                   #
#                                                      #
#  Transformations to apply to the ODD graph, in order #
#  to emulate real world use cases on arbitrary        #
#  provider maps                                       #
#                                                      #
########################################################
def no_transformations(odd_graph):
    transformed_graph = deepcopy(odd_graph)
    return transformed_graph


def change_node_ids(odd_graph):
    # tests whether method is resilient to changing node IDs, while keeping the same "topology"
    mapper = {node: "Prefix" + str(node) for node in odd_graph.nodes}
    transformed_graph = nx.relabel_nodes(deepcopy(odd_graph), mapper)
    return transformed_graph


@requires("edge_geometry")
def split_edges(odd_graph):
    # tests whether method is resilient to arbitrary edge fragmentation
    transformed_graph = deepcopy(odd_graph)
    for edge in odd_graph.edges:
        edge_data = odd_graph.get_edge_data(*edge)["data"]
        start_node = edge[0]
        end_node = edge[1]
        midpoint = find_midpoint(edge_data.geometry)
        new_node_id = transformed_graph.add_node(data=Node(coord=midpoint))
        transformed_graph.add_edge(
            start_node,
            new_node_id,
            data=create_edge(
                geometry=interpolated_geometry(
                    transformed_graph.nodes[start_node]["data"].coord, midpoint
                )
            ),
        )
        transformed_graph.add_edge(
            new_node_id,
            end_node,
            data=create_edge(
                geometry=interpolated_geometry(
                    midpoint, transformed_graph.nodes[end_node]["data"].coord
                )
            ),
        )
        transformed_graph.remove_edge(*edge)

    return transformed_graph


class GraphTestScenario(object):
    def __init__(self, name, base_graph, expected_graph, input_graph):
        """
        :param name: scenario name, as string
        :param base_graph: base graph to restrict and transform (acts as OSM reference graph)
        :param expected_graph: final graph correctly restricted to ODD
        :param input_graph: graph with restriction information which serves as input to the method
        """
        self.name = name
        self.base_graph = base_graph
        self.expected_graph = expected_graph
        self.input_graph = input_graph

    def __repr__(self):
        return self.name


def is_valid_combination(combo):
    if len(combo) == 3:
        graph = combo[0]
        transformation = combo[2]
        transform_requirements = transformation.__annotations__.get("requirements", [])

        if "edge_geometry" in transform_requirements:
            if not all(
                len(getattr(graph.get_edge_data(*edge)["data"], "geometry", [])) > 0
                for edge in graph.edges()
            ):
                return False
    return True


def generate_scenarios(
    base_graphs, restrictions, transformations, combination_function=None
):
    """
    Generates scenarios consisting of combinations of graphs, restrictions and transformations, according to logic
    defined on combination_function. By default applies all pairs combinatorial method to keep it efficient, see more
    info here: https://www.tutorialspoint.com/software_testing_dictionary/all_pairs_testing.htm
    """
    combination_function = combination_function or AllPairs

    for base_graph, restriction, transformation in combination_function(
        [base_graphs, restrictions, transformations], filter_func=is_valid_combination
    ):

        odd_graph = restriction(base_graph)
        transformed_graph = transformation(odd_graph)
        name = f"{base_graph.metadata['version']}_{restriction.__name__}_{transformation.__name__}"
        yield GraphTestScenario(name, base_graph, odd_graph, transformed_graph)


odd_restrictions = [no_restrictions, remove_node, remove_edge]
graph_transformations = [no_transformations, change_node_ids, split_edges]
graphs = [
    urban_grid_no_geometry,
    urban_grid_node_geometry,
    urban_grid_node_and_edge_geometry,
]
scenarios = generate_scenarios(graphs, odd_restrictions, graph_transformations)
