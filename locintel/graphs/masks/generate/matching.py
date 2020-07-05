import logging

from locintel.core.algorithms.itertools import pairwise, tripletwise
from locintel.core.datamodel.matching import MatchPlan, MatchWaypoint
from locintel.quality.metrics.geometry import GeometryComparator
from locintel.services.matching import MapboxMatcher


from .base import BaseMaskGenerator
from ...datamodel.jurbey import Mask
from ...processing.paths import PathsGenerator


class RouteMatchingMaskGenerator(BaseMaskGenerator):
    """
    Uses route matching to discover which elements from a base graph should be masked, given an ODD graph
    """

    def __init__(
        self,
        odd_graph,
        matcher=MapboxMatcher,
        paths_generator=PathsGenerator,
        lanes_threshold=None,
        timestamps_speed=None,
        search_radius=None,
        filter_hausdorff_distance=False,
    ):
        super().__init__("matching")
        self.odd_graph = odd_graph
        self.paths_generator = paths_generator
        self.paths = self.paths_generator(self.odd_graph).generate()
        self.matcher = matcher
        self.nodes = set()
        self.edges = set()
        self.relations = set()
        self.timestamps_speed = timestamps_speed
        self.lanes_threshold = lanes_threshold
        self.search_radius = search_radius
        self.filter_hausdorff_distance = filter_hausdorff_distance

    def generate(self):
        ignored_paths = 0
        for i, path in enumerate(self.paths):

            if self.lanes_threshold and len(path.edges) < self.lanes_threshold:
                ignored_paths += 1
                continue

            if i % 100 == 0:
                logging.info(f"Processed {i} paths")
                logging.info(f"Matched {len(self.nodes)} nodes")
                logging.info(f"Matched {len(self.edges)} edges")

            options = {}
            if self.timestamps_speed:
                options["timestamps"] = self.timestamps_speed
            if self.search_radius:
                options["radius"] = self.search_radius

            plan = MatchPlan(
                [MatchWaypoint(coord.lat, coord.lng) for coord in path.geometry]
            )
            try:
                match = self.matcher.calculate(plan, report_geometry=False, **options)
            except BaseException as e:
                logging.warning(e)
                continue

            # there's a bug in OSRM that makes the reported nodes in matches without geometries better but for
            # filtering out bad matches, we need the geometry. thus the double map match load
            if self.filter_hausdorff_distance:
                if match.metadata["raw"]["matchings"]:
                    try:
                        geom_match = self.matcher.calculate(plan, report_geometry=True)
                    except BaseException as e:
                        logging.warning(e)
                        continue

                    if self._result_is_invalid(match, geom_match, path.coords):
                        continue

            nodes, edges, relations = self._decompose_match(match)

            self.nodes.update(nodes)
            self.edges.update(edges)
            self.relations.update(relations)

        return Mask(self.nodes, self.edges, self.relations)

    def _decompose_match(self, match):
        nodes, edges, relations = set(), set(), set()
        for matching in match.metadata["raw"]["matchings"]:
            for leg in matching["legs"]:
                leg_nodes = leg["nodes"]
                nodes.update(leg_nodes)
                edges.update(pairwise(leg_nodes))
                relations.update(tripletwise(leg_nodes))
        return nodes, edges, relations

    @staticmethod
    def _result_is_invalid(match, geom_match, trace, filter_configs=None):
        filter_configs = filter_configs or [
            {"max_hausdorff_distance": 70},
            {"max_hausdorff_distance": 40, "min_confidence": 0.1},
        ]

        if not match.get("matchings"):
            return True

        confidence = match.metadata["confidence"]
        snap_distance = match.metadata["max_snap_distance"]
        num_failed_points = match.metadata["failed_points"]
        hausdorff_distance = GeometryComparator.compare(
            geom_match.geometry, trace, method="hausdorff"
        )

        for filter_config in filter_configs:
            if filter_config:
                fails_filter = True
                for filter_param in filter_config:
                    if filter_param == "min_confidence":
                        fails_filter &= confidence < filter_config["min_confidence"]
                    if filter_param == "max_snap_distance":
                        fails_filter &= (
                            snap_distance > filter_config["max_snap_distance"]
                        )
                    if filter_param == "max_num_failed_points":
                        fails_filter &= (
                            num_failed_points > filter_config["max_num_failed_points"]
                        )
                    if filter_param == "max_hausdorff_distance":
                        fails_filter &= (
                            hausdorff_distance > filter_config["max_hausdorff_distance"]
                        )

                if fails_filter:
                    return True
        return False
