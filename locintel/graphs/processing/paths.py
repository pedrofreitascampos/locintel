import json

import networkx as nx

from das.routing.core.datamodel.geo import GeoCoordinate, Geometry
from das.routing.graphs.datamodel.jurbey import Path


class PathsGenerator:
    def __init__(self, graph, minimum_path_length=6):
        self.graph = graph
        self.minimum_path_length = minimum_path_length

    def generate(self):
        edges = list(nx.edge_dfs(self.graph))

        paths, short_paths = self._create_paths(edges)

        new_paths = self._add_extra_paths(self.graph, short_paths)
        paths.extend(new_paths)

        geometry_paths = []
        for path in paths:
            coords, hd_lane_ids = self._get_coord_mapping(self.graph, path)

            if coords and hd_lane_ids:
                geometry_paths.append(Path(coords, hd_lane_ids))

        return geometry_paths

    @staticmethod
    def export_geometries(paths, file_name="data/geometries.geojson"):
        geojson = {"type": "FeatureCollection", "features": []}

        for path in paths:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[point[1], point[0]] for point in path.coords],
                },
                "properties": path.edges,
            }

            geojson["features"].append(feature)

        with open(file_name, "wb") as f:
            f.write(json.dumps(geojson).encode("utf-8"))

    def _create_paths(self, edges):
        paths = []
        short_paths = []

        path = [edges[0]]
        end_node = edges[0][-1]

        for edge in edges[1:]:
            last_node_in_path = end_node
            start_node, end_node = edge

            if start_node == last_node_in_path:
                # there is connectivity, extend path
                path.append(edge)
            else:
                self._add_path(paths, short_paths, path)
                path = [edge]

        self._add_path(paths, short_paths, path)

        return paths, short_paths

    def _add_path(self, paths, short_paths, path):
        if len(path) >= self.minimum_path_length:
            paths.append(path)
        else:
            short_paths.append(path)

    def _add_extra_paths(self, graph, short_paths):
        paths = []
        for edges in short_paths:

            first_node = edges[0][0]
            last_node = edges[-1][-1]

            predecessors = self._get_next_nodes(first_node, graph.predecessors)
            successors = self._get_next_nodes(last_node, graph.successors)

            rev_nodes = list(reversed(predecessors))
            orig_nodes = [edge[0] for edge in edges][1:]

            nodes = rev_nodes + orig_nodes + successors
            path = list(zip(nodes, nodes[1:]))
            for link in path:
                assert graph.has_edge(link[0], link[1])

            paths.append(path)
        return paths

    def _get_coord_mapping(self, graph, path):
        nodes = graph.nodes

        hd_lane_ids, transition_lane = self._collect_hd_lanes(graph, path)
        if len(hd_lane_ids) == 0:
            # path contains only lane changes
            return None, None

        coords = self._collect_geo(nodes, path, transition_lane)

        assert len(coords) == len(hd_lane_ids) + 1

        return coords, hd_lane_ids

    @staticmethod
    def _collect_hd_lanes(graph, path):
        hd_lane_ids = []
        transition_lane = []
        edge_data_table = nx.get_edge_attributes(graph, "data")
        for index, edge in enumerate(path):

            # lane changes don't have HD Lane IDs
            if edge and "hd_lane_id" in edge_data_table[edge].metadata:
                hd_lane_ids.append(edge_data_table[edge].metadata["hd_lane_id"])
            else:
                transition_lane.append(index)

        return hd_lane_ids, transition_lane

    @staticmethod
    def _collect_geo(nodes, path, transition_lane):
        geo = Geometry(
            [
                GeoCoordinate(
                    nodes[pair[0]]["data"].coord.lat, nodes[pair[0]]["data"].coord.lng
                )
                for index, pair in enumerate(path)
                if index not in transition_lane
            ]
        )

        # Adds the last coordinate for last node
        geo.coords += [
            GeoCoordinate(
                nodes[path[-1][1]]["data"].coord.lat,
                nodes[path[-1][1]]["data"].coord.lng,
            )
        ]
        return geo

    @staticmethod
    def _get_next_nodes(node, func):
        neighbours = [node]
        nodes = []
        while neighbours:
            for node in neighbours:
                neighbours = list(func(node))
                if neighbours:
                    break
            if node in nodes or len(nodes) > 5:
                break

            nodes.append(node)
        return nodes
