"""
Methods to test ODD generation methods

To add a method for testing, define the method setup class:
    1. Subclass `BaseODDMethod`
    2. Override the `setup` method, which transforms pure graph into artifacts required for the generation method
    3. Override the `apply` method, which applies the method based on required artifacts produced in `setup`.
    4. Override the `teardown` method, which cleans up your stuff

See examples below.
"""
from copy import deepcopy
import glob
import os

from das.routing.graphs.datamodel.jurbey import Jurbey
from das.routing.graphs.adapters.osm import OsmAdapter
from das.routing.graphs.masks.apply.osm import ApplyMaskOsmMixin
from das.routing.graphs.masks.generate.matching import RouteMatchingMaskGenerator
from das.routing.services.matching import DasMatcher

from .setup_utils import start_routing_server, stop_container


class BaseODDMethodDriver(object):
    def __init__(self, name):
        self.name = name

    @staticmethod
    def setup(base_graph, odd_graph):
        """
        Function which sets-up the method, by transforming base graph and odd graph created from "scenarios"
        """
        raise NotImplementedError("Implement subclass")

    @staticmethod
    def apply(base_artifact, odd_artifact):
        """
        Function which applies the method, requires an artifact referring to the base map (method source) and
        an artifact referring to the odd graph (method target)
        """
        raise NotImplementedError("Implement subclass")

    @staticmethod
    def teardown(*arg, **kwargs):
        """
        Clean your stuff
        """
        raise NotImplementedError("Implement subclass")


class SimpleGraphMatchingDriver(BaseODDMethodDriver):
    def __init__(self):
        super().__init__("simple_graph_matching")

    @staticmethod
    def setup(base_graph, odd_graph):
        # this will typically involve more complex stuff, like base_graph to OSM.PBF transformations, etc.
        return base_graph, odd_graph

    @staticmethod
    def apply(base_artifact, odd_artifact):
        result = deepcopy(base_artifact)
        for edge in base_artifact.edges:
            if edge not in odd_artifact.edges:
                result.remove_edge(*edge)
                print(f"removing {edge}")

        for node in base_artifact.nodes:
            if node not in odd_artifact.nodes:
                result.remove_node(node)
                print(f"removing {node}")

        return result

    @staticmethod
    def teardown(*arg, **kwargs):
        return


class RouteMatchingMethodDriver(BaseODDMethodDriver):
    """
    Matches ODD graph geometries to matching service running on osm.pbf base map
    """

    def __init__(
        self,
        base_map_filename="data/data.osm.pbf",
        odd_filename="test.jurbey",
        output_path="data",
    ):
        super().__init__("route_matching")
        self.base_map_filename = base_map_filename
        self.odd_filename = odd_filename
        self.output_path = output_path

    def setup(self, base_graph, odd_graph):
        # Convert base graph to osm.pbf and start server
        base_graph.to_osm_pbf(self.base_map_filename)
        self.process_handler, url = start_routing_server()
        self.base_graph = deepcopy(base_graph)

        odd_graph.to_pickle(self.odd_filename)

        return url, self.odd_filename

    def apply(self, base_artifact, odd_artifact):
        """
        base_artifact: endpoint to matching service
        odd_artifact: ODD represented as Jurbey
        """
        odd_graph = Jurbey.from_pickle(odd_artifact)
        graph_matcher = RouteMatchingMaskGenerator(
            odd_graph, DasMatcher(endpoint=base_artifact), hd_mapping=False
        )
        mask = graph_matcher.generate()
        adapter = OsmAdapter(self.base_map_filename, processors=ApplyMaskOsmMixin)
        adapter.apply_mask(mask)
        return adapter.get_jurbey()

    def teardown(self, keep_artifacts=False):
        self.process_handler.terminate()
        if not keep_artifacts:
            os.remove(self.base_map_filename)
            for f in glob.glob(
                f'{os.path.join(os.path.dirname(self.base_map_filename), "*osrm*")}'
            ):
                os.remove(f)
            os.remove(self.odd_filename)

        stop_container()
