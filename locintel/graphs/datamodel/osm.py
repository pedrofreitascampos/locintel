from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Dict

import osmium

from das.routing.core.datamodel.geo import GeoCoordinate
from das.routing.graphs.datamodel.types import SignType, RoadClass


@dataclass
class Node:
    id: int
    coord: GeoCoordinate
    ways: List[int] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_osm(self):
        osm_node = osmium.osm.mutable.Node()
        osm_node.id = self.id
        osm_node.location = osmium.osm.Location(self.coord.lng, self.coord.lat)

        metadata = deepcopy(self.metadata)
        osm_node.version = metadata.pop("version")
        osm_node.tags = _create_tags_list(metadata)

        return osm_node


NodeRef = namedtuple("NodeRef", "ref")


@dataclass
class Way:
    id: int
    nodes: List[int] = field(default_factory=list)
    tags: Dict = field(default_factory=dict)

    def to_osm(self):
        osm_way = osmium.osm.mutable.Way()
        osm_way.id = self.id

        nodes = []
        for node_id in self.nodes:
            node = NodeRef(node_id)
            nodes.append(node)

        osm_way.nodes = nodes

        tags = deepcopy(self.tags)
        osm_way.version = tags.pop("version")
        osm_way.tags = _create_tags_list(tags)

        return osm_way


ViaNode = namedtuple("ViaNode", "id")
ViaWays = namedtuple("ViaWay", ("id", "ways"))
RelationMember = namedtuple("RelationMember", ("type", "role", "ref"))


@dataclass
class Relation:
    id: int = None
    from_way: int = None
    from_node: int = None
    to_way: int = None
    to_node: int = None
    via: namedtuple = None
    tags: Dict = field(default_factory=dict)

    def to_osm(self):
        osm_relation = osmium.osm.mutable.Relation()
        osm_relation.members = [RelationMember("w", "from", self.from_way)]

        if isinstance(self.via, ViaNode):
            osm_relation.members.append(RelationMember("n", "via", self.via.id))
        else:
            osm_relation.members.extend(
                [RelationMember("w", "via", via_way) for via_way in self.via.ways]
            )

        osm_relation.members.append(RelationMember("w", "to", self.to_way))

        osm_relation.id = self.id

        tags = deepcopy(self.tags)
        osm_relation.version = tags.pop("version")
        osm_relation.tags = _create_tags_list(tags)
        osm_relation.visible = True

        return osm_relation


@dataclass
class Sign:
    signType: SignType
    coord: GeoCoordinate = field(default_factory=GeoCoordinate)
    value: int = -1


access_tag_blacklist = {
    "no",
    "agricultural",
    "forestry",
    "customers",
    "private",
    "delivery",
    "destination",
}
highway_blacklist = {
    "footway",
    "path",
    "track",
    "bridleway",
    "pedestrian",
    "steps",
    "cycleway",
    "elevator",
    "construction",
    "abandoned",
}
speed_dict = {
    "motorway": 90,
    "motorway_link": 45,
    "trunk": 85,
    "trunk_link": 40,
    "primary": 65,
    "primary_link": 30,
    "secondary": 55,
    "secondary_link": 25,
    "tertiary": 40,
    "tertiary_link": 20,
    "unclassified": 25,
    "residential": 25,
    "living_street": 10,
    "service": 15,
}

road_class = {
    "motorway": RoadClass.Highway,
    "motorway_link": RoadClass.Highway,
    "trunk": RoadClass.Highway,
    "trunk_link": RoadClass.Highway,
    "primary": RoadClass.MajorRoad,
    "primary_link": RoadClass.MajorRoad,
    "secondary": RoadClass.MajorRoad,
    "secondary_link": RoadClass.MajorRoad,
    "tertiary": RoadClass.LocalRoad,
    "tertiary_link": RoadClass.LocalRoad,
    "unclassified": RoadClass.LocalRoad,
    "residential": RoadClass.LocalRoad,
    "service": RoadClass.DirtRoad,
    "living_street": RoadClass.DirtRoad,
}

Tag = namedtuple("Tag", ("k", "v"))


class TagList:

    """ Class that mimics osmium's TagList.
    """

    def __init__(self):
        self.tags_list = []

    def __contains__(self, other):
        return any(other == tag.k for tag in self.tags_list)

    def __iter__(self):
        return iter(self.tags_list)

    def __getitem__(self, item):
        for tag in self.tags_list:
            if tag.k == item:
                return tag.v

    def append(self, item):
        self.tags_list.append(item)


def _create_tags_list(tags_dict):
    tags = TagList()
    for tag_id, tag_v in tags_dict.items():
        if tag_id != "hd_edges":
            tag = Tag(tag_id, tag_v)

            tags.append(deepcopy(tag))

    return tags


osm_class = {
    "motorway": RoadClass.Highway,
    "motorway_link": RoadClass.Highway,
    "trunk": RoadClass.Highway,
    "trunk_link": RoadClass.Highway,
    "primary": RoadClass.MajorRoad,
    "primary_link": RoadClass.MajorRoad,
    "secondary": RoadClass.MajorRoad,
    "secondary_link": RoadClass.MajorRoad,
    "tertiary": RoadClass.LocalRoad,
    "tertiary_link": RoadClass.LocalRoad,
    "unclassified": RoadClass.LocalRoad,
    "residential": RoadClass.LocalRoad,
    "service": RoadClass.DirtRoad,
    "living_street": RoadClass.DirtRoad,
}
