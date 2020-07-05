from copy import deepcopy
from collections import defaultdict
from dataclasses import dataclass, field
import json
import os
import osmium
import pickle
from typing import List, Dict, Set, Tuple, Any

from haversine import haversine
import networkx as nx

from locintel.core.datamodel.geo import Geometry, GeoCoordinate

from ..datamodel.osm import Sign
from ..processing.transform import compact_graph
from .types import EdgeType, RestrictionType, RoadClass, RoadAccessibility, VehicleType


@dataclass
class Node:
    coord: GeoCoordinate
    id: Any = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Edge:
    type: EdgeType
    from_node: int
    to_node: int
    road_class: RoadClass = None
    road_accessibility: RoadAccessibility = None
    vehicle_accessibility: List[VehicleType] = field(default_factory=list)
    geometry: Geometry = field(default_factory=list)
    signs: List[Sign] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_osm_way(self):
        w = osmium.osm.mutable.Way()
        w.nodes = [self.from_node, self.to_node]
        w.tags = self.metadata
        return w


@dataclass
class Restriction:
    type: RestrictionType
    edges: List[Edge]


@dataclass
class Path:
    geometry: Geometry = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class Mask:
    nodes: Set[int] = field(default_factory=set)
    edges: Set[Tuple] = field(default_factory=set)
    relations: Set[Tuple] = field(default_factory=set)
    hd_mapping: Dict = field(default_factory=list)


class Jurbey(nx.DiGraph):
    """
    mapbox-routing internal, provider-agnostic representation for graphs
    """

    def __init__(self, nodes=None, edges=None, restrictions=None, metadata=None):
        nx.DiGraph.__init__(self)
        self.add_nodes_from(nodes or [])
        self.add_edges_from(edges or [])
        self.restrictions = restrictions or []
        self.metadata = metadata or {}

    def __eq__(self, other):
        return (
            self.edges == other.edges
            and self.nodes == other.nodes
            and self.restrictions == other.restrictions
        )

    def __str__(self):
        edge_data_table = nx.get_edge_attributes(self, "data")
        real_edges = [
            (edge, edge_data_table[edge].metadata["hd_lane_id"])
            for edge in edge_data_table
            if "hd_lane_id" in edge_data_table[edge].metadata
        ]

        return f"Jurbey=(nodes={len(self.nodes)}, edges={len(real_edges)}, hd_edges={len(self.edges)})"

    def __repr__(self):
        return f"Jurbey=(nodes={self.nodes}, edges={self.edges}, restrictions={self.restrictions})"

    def add_node(self, data, *arg, **kwargs):
        """
        Override nx.add_node in order to create new node id when adding a new node
        """
        new_node_id = max(self.nodes) + 1 if self.nodes else 0
        super().add_node(new_node_id, data=data)
        return new_node_id

    def distance(self, n1, n2):
        """
        Calculates distance in meters for the optimal path between two connected nodes in the graph.
        """
        dist = 0.0
        edge = self.edges[n1, n2]
        geo = edge["data"].geometry.to_lat_lng_tuples()
        for seg in zip(geo, geo[1:]):
            dist += haversine(*seg)
        return 1000.0 * dist

    def is_healthy(self):
        """This method performs a set of checks over the graph to detect some
            possible mapping errors

        Returns:
            Boolean saying if no error was detected

        """
        is_healthy = nx.is_strongly_connected(self)
        return is_healthy

    def draw(self, node_size=20, arrowsize=3):
        pos = {}
        edge_color = [
            "b" if e[2]["data"].type.value.startswith("CONNECTION") else "g"
            for e in self.edges(data=True)
        ]
        for n in self.nodes(data=True):
            coord = n[1]["data"].coord
            pos[n[0]] = (coord.lng, coord.lat)
        nx.draw_networkx(
            self,
            pos,
            with_labels=False,
            node_size=node_size,
            edge_color=edge_color,
            alpha=0.5,
            arrowsize=arrowsize,
        )

    def to_pickle(self, output_path):
        with open(output_path, "w") as f:
            return pickle.dump(self, f)

    def to_graphml(self, output_path="data/graph.ml"):
        with open(output_path, "w") as f:
            f.write(nx.generate_graphml(compact_graph(self), encoding="utf-8"))

    def to_osm_pbf(self, pbf_path="data/data.osm.pbf", overwrite=True):
        counter = defaultdict(int)

        if overwrite and os.path.exists(pbf_path):
            os.remove(pbf_path)

        writer = osmium.SimpleWriter(pbf_path)

        for node in self.nodes.values():
            writer.add_node(node.to_osm())
            counter["nodes"] += 1

        for edge in self.edges.values():
            writer.add_way(edge.to_osm_way())
            counter["ways"] += 1

        for relation in getattr(self, "relations", {}).values():
            writer.add_relation(relation.to_osm())
            counter["relations"] += 1

        writer.close()

    def to_geojson(self, output_path="data/graph.geojson", compact_format=False):
        geojson = {"type": "FeatureCollection", "features": []}
        for n in self.nodes(data=True):
            lng = n[1]["data"].coord.lng
            lat = n[1]["data"].coord.lat
            uuid = n[1]["data"].metadata.get("uuid", "No UUID")
            color = ""
            if uuid == -1:
                color = "#1F0E15"
            n_dict = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "uuid": uuid,
                    "marker-color": color,
                    "marker-symbol": "marker",
                },
            }
            geojson["features"].append(n_dict)
        for e in self.edges(data=True):
            edge_color = "red"  # LANE_STRAIGHT
            if e[2]["data"].edgeType.value.startswith("CONNECTION"):
                edge_color = "green"
            elif e[2]["data"].edgeType.value.startswith("LANE_CHANGE"):
                edge_color = "blue"
            e_geometry = e[2]["data"].geometry

            if len(e_geometry) > 0 and not compact_format:
                coordinates_array = e_geometry.to_lng_lat_tuples()
            else:
                # fallback to using node geoms, if no geom explicitly provided
                lng0 = self.nodes[e[0]]["data"].coord.lng
                lat0 = self.nodes[e[0]]["data"].coord.lat
                lng1 = self.nodes[e[1]]["data"].coord.lng
                lat1 = self.nodes[e[1]]["data"].coord.lat
                coordinates_array = [[lng0, lat0], [lng1, lat1]]
            signs = deepcopy(e[2]["data"].signs)

            properties = deepcopy(e[2]["data"].metadata)
            properties["type"] = e[2]["data"].edgeType.value
            properties["uuid"] = e[2]["data"].metadata.get("uuid", "No UUID")
            if len(signs) > 0:
                properties["speed"] = signs[0].value
            properties["stroke"] = edge_color
            properties["stroke-width"] = 2
            n_dict = {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coordinates_array},
                "properties": properties,
            }

            geojson["features"].append(n_dict)
        with open(output_path, "w") as f:
            json.dump(geojson, f)

    @classmethod
    def from_pickle(cls, pickle_path):
        with open(pickle_path, "r") as f:
            return pickle.load(f)
