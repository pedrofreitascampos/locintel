import networkx as nx
import logging
import osmium
import re

from das.routing.core.datamodel.geo import GeoCoordinate, Geometry

from .base import BaseAdapter
from ..datamodel.jurbey import Edge, Node
from ..datamodel.osm import (
    access_tag_blacklist,
    highway_blacklist,
    speed_dict,
    road_class,
)
from ..datamodel.types import EdgeType, VehicleType, RoadClass, RoadAccessibility
from ..masks.apply.osm import ApplyMaskOsmMixin


class OsmAdapter(BaseAdapter, osmium.SimpleHandler):
    """
    Adapts OSM data to internal representation
    """

    def __init__(self, osm_filename):
        BaseAdapter.__init__(self, metadata={"provider": "OSM"})
        osmium.SimpleHandler.__init__(self)

        self.nodes = {}
        self.node_ids = set()

        self.apply_file(osm_filename)

    def get_jurbey(self, *arg, **kwargs):
        # Filtering nodes out
        self._prepare_nodes()

        # Generating geometries for arcs
        self._prepare_edges()

        logging.info(nx.info(self.G).replace("\n", " "))

        return self.G

    def node(self, n):
        """
        Node callback logic to osmium.SimpleHandler
        """
        geo = GeoCoordinate(lng=n.location.lon, lat=n.location.lat)
        metadata = dict(
            version=n.version,
            **{tag.k: tag.v for tag in n.tags},
            hd_edges=self.hd_mapping.get(n.id, [])
            if hasattr(self, "hd_mapping")
            else [],
        )
        node_data = Node(id=n.id, coord=geo, metadata=metadata)
        self.nodes[n.id] = node_data

    def way(self, w):
        """
        Way callback logic to osmium.SimpleHandler
        """
        access_blacklisted = any(
            e in w.tags and w.tags[e] == "yes" for e in access_tag_blacklist
        ) or any(
            "access" in w.tags and w.tags["access"] == e for e in access_tag_blacklist
        )

        if (
            "highway" in w.tags
            and not access_blacklisted
            and w.tags["highway"] not in highway_blacklist
        ):
            for n in w.nodes:
                self.node_ids.add(n.ref)
            pairs = zip(list(w.nodes), list(w.nodes)[1:])
            for p in pairs:
                # set default based on hwy type
                maxspeed = speed_dict.get(w.tags["highway"], -1)

                # try to parse maxspeed tag
                if "maxspeed" in w.tags:
                    matched = re.compile("(\d+)(?P<mph> mph)?$").match(
                        w.tags["maxspeed"]
                    )
                    if matched:
                        if matched.group("mph"):
                            maxspeed = int(matched.group(1)) * 1.609
                        maxspeed = float(matched.group(1))

                self._add_edge(p[0].ref, p[1].ref, w, maxspeed)

                oneway = "oneway" in w.tags and w.tags["oneway"] in ["yes", "true", "1"]
                if not oneway:
                    self._add_edge(p[1].ref, p[0].ref, w, maxspeed)

    def relation(self, r):
        """
        Relation callback logic to osmium.SimpleHandler
        """
        restriction = False
        if "type" in r.tags:
            restriction = r.tags["type"].startswith("restriction")
        restriction = restriction or "restriction" in r.tags
        if restriction:
            f, via, t = None, None, None
            for m in r.members:
                if m.role == "from":
                    f = m.ref
                elif m.role == "to":
                    t = m.ref
                elif m.role == "via" and m.type == "n":
                    # TODO Handle Uturn no straight no left
                    pass

    def _prepare_nodes(self):
        self.nodes = {k: v for k, v in self.nodes.items() if k in self.node_ids}
        nx.set_node_attributes(self.G, self.nodes, "data")

    def _prepare_edges(self):
        for e in self.G.edges(data=True):
            if self.G.nodes[e[0]] and self.G.nodes[e[1]]:
                geo0 = self.G.nodes[e[0]]["data"].coord
                geo1 = self.G.nodes[e[1]]["data"].coord
                e[2]["data"].geometry = Geometry([geo0, geo1])
            else:
                logging.warning(
                    f"Missing data for edge {self.G.nodes[e[0]]} or {self.G.nodes[e[1]]}"
                )

    def _add_edge(self, p0_ref, p1_ref, w, maxspeed):
        if self.G.has_edge(p0_ref, p1_ref):
            self.G[p0_ref][p1_ref]["way"].append(w.id)
            self.G[p0_ref][p1_ref]["data"].type = EdgeType.CONNECTION_STRAIGHT
        else:
            edge_data = Edge(
                EdgeType.LANE_STRAIGHT,
                p0_ref,
                p1_ref,
                road_class.get(w.tags["highway"], RoadClass.DirtRoad),
                RoadAccessibility.NoRestriction,
                vehicle_accessibility=[VehicleType.All],
                metadata={tag.k: tag.v for tag in w.tags},
            )
            self.G.add_edge(
                p0_ref,
                p1_ref,
                way=[w.id],
                speed=maxspeed,
                rate=1,
                direction=0,
                data=edge_data,
            )


class OsmAdapterWithMask(OsmAdapter, ApplyMaskOsmMixin):
    def __init__(self, osm_filename):
        OsmAdapter.__init__(self, osm_filename)
        ApplyMaskOsmMixin.__init__(self)
