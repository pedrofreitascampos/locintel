from copy import copy
import json

from locintel.core.datamodel.geo import GeoCoordinate

from .base import BaseAdapter
from ..datamodel.jurbey import Edge, Node
from ..datamodel.types import EdgeType, RoadClass, RoadAccessibility, VehicleType

ACCEPTED_LINETYPES = ["BROKEN", "NO_LANE"]
NODE_DIRECTION_TRANSLATOR = {"from_edges": "to_node", "to_edges": "from_node"}


class DeepmapAdapter(BaseAdapter):
    """
    DeepMap adapter, this is known to not work perfectly in its current state,
    needs tests and further development to be in safe state
    """

    def __init__(self, deepmap_file):
        super().__init__(metadata={"provider": "Deepmap"})
        with open(deepmap_file, "r") as fp:
            self.data = json.load(fp)

        self.edges = {}
        self.lane_changes = {}
        self.edge_metadata = {"oneway": "yes", "highway": "primary"}

    def get_jurbey(self, add_virtual_lanes=True):
        for lane in self.data:
            edge = self._get_edge(lane)

            if not edge["car_allowed"]:
                continue

            from_node, to_node = self._get_edge_nodes(edge)
            if from_node is None:
                from_node = self._create_node(edge["geometry"][0])
            if to_node is None:
                to_node = self._create_node(edge["geometry"][-1])

            # Add current edge and respective node connections
            self.edges.update(
                {edge["id"]: {"from_node": from_node, "to_node": to_node}}
            )

            # Update neighbouring edges' nodes
            list(
                map(
                    lambda e: self.edges.setdefault(e, {"to_node": from_node}),
                    edge["from_edges"],
                )
            )
            list(
                map(
                    lambda e: self.edges.setdefault(e, {"from_node": to_node}),
                    edge["to_edges"],
                )
            )

            metadata = copy(self.edge_metadata)
            metadata.update({"hd_lane_id": str(edge["id"])})

            self.G.add_edge(
                from_node,
                to_node,
                data=Edge(
                    EdgeType.LANE_STRAIGHT,
                    from_node,
                    to_node,
                    RoadClass.MajorRoad,
                    RoadAccessibility.NoRestriction,
                    vehicle_accessibility=[VehicleType.Car],
                    geometry=edge["geometry"],
                    metadata=metadata,
                ),
            )

            # Add virtual lane
            self.lane_changes.update({edge["id"]: edge["neighbours"]})

        if add_virtual_lanes:
            self._connect_virtual_lanes()

        return self.G

    def _get_edge(self, lane):
        return {
            "id": lane["id"],
            "from_edges": lane["fromLaneIdsList"],
            "to_edges": lane["toLaneIdsList"],
            "geometry": list(
                map(
                    lambda x: GeoCoordinate(float(x["lng"]), float(x["lat"])),
                    lane["centerLine"]["geometry"],
                )
            ),
            "car_allowed": "CAR"
            in lane["restrictions"].get("allowedVehicleTypesList", []),
            "neighbours": self._get_lanes_changes(lane),
        }

    def _get_edge_nodes(self, edge):
        from_node = self._get_node(edge["id"], "from_node")
        if from_node is None:
            from_node = self._find_node_from_connections(edge, "from_edges")

        to_node = self._get_node(edge["id"], "to_node")
        if to_node is None:
            to_node = self._find_node_from_connections(edge, "to_edges")

        return from_node, to_node

    def _get_node(self, edge_id, which):
        try:
            return self.edges[edge_id][which]
        except KeyError:
            return None

    def _find_node_from_connections(self, edge, direction):
        for edge_id in edge[direction]:
            node = self._get_node(edge_id, NODE_DIRECTION_TRANSLATOR[direction])
            if node:
                return node
        return None

    def _create_node(self, coord):
        node_id = self.G.add_node(data=Node(coord=coord))
        self.G.nodes[node_id]["data"].metadata = {"uuid": node_id}
        return node_id

    def _connect_virtual_lanes(self):
        for lane_id, target_lanes in self.lane_changes.items():
            for l in target_lanes:
                try:
                    self.G.add_edge(
                        self.edges[lane_id]["from_node"],
                        self.edges[l]["from_node"],
                        data=Edge(
                            EdgeType.LANE_CHANGE,
                            self.edges[lane_id]["from_node"],
                            self.edges[lane_id]["to_node"],
                            RoadClass.LocalRoad,
                            RoadAccessibility.NoRestriction,
                            vehicle_accessibility=[VehicleType.Car],
                            metadata=self.edge_metadata,
                        ),
                    )
                except KeyError:
                    pass

    @staticmethod
    def _get_lanes_changes(lane):
        return [
            l
            for l in lane["leftLanesList"]
            if lane["leftBoundaryLine"].get("lineType", "NO_LANE") in ACCEPTED_LINETYPES
        ] + [
            l
            for l in lane["rightLanesList"]
            if lane["rightBoundaryLine"].get("lineType", "NO_LANE")
            in ACCEPTED_LINETYPES
        ]
