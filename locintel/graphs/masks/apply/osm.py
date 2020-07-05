from copy import deepcopy

from ordered_set import OrderedSet
import networkx as nx

from locintel.core.algorithms.geo import create_vector, calculate_direction
from locintel.core.algorithms.itertools import pairwise
from locintel.core.datamodel.geo import GeoCoordinate

from ...datamodel.osm import Way, ViaNode, ViaWays, Relation
from ...datamodel.jurbey import Edge, Node, Jurbey
from ...datamodel.types import EdgeType, RoadClass, RoadAccessibility
from ...masks.apply.base import ApplyMaskBase
from ...processing.utils import find_common_node, sort_nodes, get_adjacent_node


class ApplyMaskOsmMixin(ApplyMaskBase):
    """
    Extension to locintel.graphs.adapters.osm.OsmAdapter which applies generated mask modifications at OSM load time
    """

    def __init__(self):
        super(ApplyMaskBase).__init__()
        self.mask = None
        # don't overwrite underlying OSM data if it already exists
        self.G = getattr(self, "G", Jurbey())
        self.nodes = getattr(self, "nodes", {})
        self.ways = getattr(self, "ways", {})
        self.relations = getattr(self, "relations", {})

    def apply_mask(self, mask):
        self.mask = mask
        self._filter_nodes()
        self._filter_ways()
        self._find_restrictions()
        self._transform_ways(list(self.relations.keys()))

        for edge in mask.edges:
            self._find_or_add_edge(edge[0], edge[1], None)

        # Filtering nodes out
        self._prepare_nodes()

        # Generating geometries for edges
        self._prepare_edges()

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
        node_ids = [node.ref for node in w.nodes]

        if "highway" in w.tags and (
            any(pair in self.mask.edges for pair in pairwise(node_ids))
            or any(
                pair in self.mask.edges for pair in pairwise(list(reversed(node_ids)))
            )
        ):
            tags = dict(version=w.version, **{tag.k: tag.v for tag in w.tags})

            self.ways[w.id] = Way(w.id, node_ids, tags=tags)

    def relation(self, r):
        restriction = False
        if "type" in r.tags:
            restriction = r.tags["type"].startswith("restriction")
        restriction |= "restriction" in r.tags

        if restriction:
            from_way, via, to_way = (None,) * 3
            exists = True
            for m in r.members:
                if m.role == "from":
                    from_way = m.ref
                    exists &= from_way in self.ways
                elif m.role == "to":
                    to_way = m.ref
                    exists &= to_way in self.ways
                elif m.role == "via" and m.type == "n":
                    via = ViaNode(m.ref)
                    exists &= via.id in self.nodes
                elif m.role == "via" and m.type == "w":
                    if m.ref not in self.ways:
                        exists = False
                        continue
                    else:
                        via_ways = via.ways if via else []
                        via_nodes = via.id if via else []

                        via_ways.append(m.ref)
                        via_nodes = sort_nodes(list(via_nodes), self.ways[m.ref].nodes)

                        via = ViaWays(via_nodes, via_ways)

            if exists and from_way and to_way and via:

                from_node = (
                    get_adjacent_node(self.ways[from_way].nodes, via.id)
                    if isinstance(via, ViaNode)
                    else get_adjacent_node(
                        self.ways[from_way].nodes,
                        find_common_node(self.ways[from_way].nodes, via.id),
                    )
                )
                to_node = (
                    get_adjacent_node(self.ways[to_way].nodes, via.id)
                    if isinstance(via, ViaNode)
                    else get_adjacent_node(
                        self.ways[to_way].nodes,
                        find_common_node(self.ways[to_way].nodes, via.id),
                    )
                )

                if not from_node or not to_node:
                    return

                tags = dict(version=r.version, **{tag.k: tag.v for tag in r.tags})

                key = (from_node, via.id, to_node)

                self.relations[key] = Relation(
                    id=r.id,
                    from_way=from_way,
                    from_node=from_node,
                    to_way=to_way,
                    to_node=to_node,
                    via=via,
                    tags=tags,
                )

            return

    def _filter_nodes(self):
        # this logic should be merged with node callback
        self.nodes = {
            node_id: node
            for node_id, node in self.nodes.items()
            if node_id in self.mask.nodes
        }

    def _prepare_nodes(self):

        nx.set_node_attributes(self.G, self.nodes, "data")

    def _prepare_edges(self):
        for e in self.G.edges(data=True):
            geo0 = self.G.nodes[e[0]]["data"].coord
            geo1 = self.G.nodes[e[1]]["data"].coord
            e[2]["data"].geometry = [geo0, geo1]

    def _find_or_add_edge(self, node_1, node_2, max_speed):

        if not self.G.has_edge(node_1, node_2):
            edge_data = Edge(
                EdgeType.LANE_STRAIGHT,
                node_1,
                node_2,
                road_class=RoadClass.Highway,
                road_accessibility=RoadAccessibility.NoRestriction,
                metadata={},
            )
            self.G.add_edge(
                node_1, node_2, way=None, speed=max_speed, rate=1, data=edge_data
            )

    @staticmethod
    def __split_paths(edges):
        paths = []

        path = [edges[0]]
        end_node = edges[0][-1]

        for edge in edges[1:]:
            last_node_in_path = end_node
            start_node, end_node = edge

            if start_node == last_node_in_path:
                # there is connectivity, extend path
                path.append(edge)
            else:
                paths.append(path)
                path = [edge]

        paths.append(path)

        return paths

    @staticmethod
    def __edges_to_set(pairs, mask_edges=()):
        nodes = OrderedSet()

        for pair in pairs:
            if pair in mask_edges:
                nodes.update(pair)

        return nodes

    @staticmethod
    def __invert_edges(edges):
        return OrderedSet(reversed([edge[::-1] for edge in edges]))

    def _transform_ways(self, relation_ids):
        for relation_id in relation_ids:

            relation = self.relations[relation_id]

            is_via_node = isinstance(relation.via, ViaNode)

            # TODO: Handle ViaWay case when we handle creating new ones
            if is_via_node:

                relation_is_valid = self.__is_relation_valid(
                    relation.via.id, relation.from_way, relation.from_node
                ) and self.__is_relation_valid(
                    relation.via.id, relation.to_way, relation.to_node
                )

                if not relation_is_valid:
                    del self.relations[relation_id]
                    continue

                self.__split_way_at_restriction(relation_id, relation.from_way)
                self.__split_way_at_restriction(relation_id, relation.to_way)

        for way_id, way in list(self.ways.items()):
            if not way.nodes:
                del self.ways[way_id]
                continue

    def _filter_ways(self):
        ways = deepcopy(self.ways)
        for way in ways.values():

            filtered_ways = self.__filter_way(way, self.mask.edges)
            for filtered_way in filtered_ways:
                self.ways[filtered_way.id] = filtered_way

                for node_id in filtered_way.nodes:
                    assert node_id in self.nodes, f"{node_id} not found"
                    self.nodes[node_id].ways.append(filtered_way.id)

    def __filter_way(self, way, mask_edges):
        oneway = "oneway" in way.tags and way.tags["oneway"] not in ["no", "0", "false"]

        if oneway:
            reverse = way.tags["oneway"] in ["-1", "reverse"]

            way_nodes = way.nodes if not reverse else reversed(way.nodes)
            nodes = self.__edges_to_set(pairwise(way_nodes), mask_edges)
            way.nodes = nodes.items

            if reverse:
                way.tags["oneway"] = "yes"

        else:
            edges = OrderedSet(
                [edge for edge in pairwise(way.nodes) if edge in mask_edges]
            )
            reversed_edges = OrderedSet(
                [
                    edge
                    for edge in pairwise(list(reversed(way.nodes)))
                    if edge in mask_edges
                ]
            )

            reversed_reversed_edges = OrderedSet(
                [edge[::-1] for edge in reversed(reversed_edges)]
            )

            if edges == reversed_reversed_edges:
                way.nodes = self.__edges_to_set(edges, mask_edges).items
            else:
                return self.__handle_non_matching_directions(
                    edges, reversed_edges, reversed_reversed_edges, way, mask_edges
                )

        return [way]

    def __split_way(self, way, via_node):

        original_nodes = way.nodes

        index = way.nodes.index(via_node)

        way_1_nodes = way.nodes[: index + 1]
        way_2_nodes = way.nodes[index:]

        new_way_id = max(self.ways.keys()) + 1

        self.ways[way.id].nodes = way_1_nodes
        self.ways[new_way_id] = Way(new_way_id, way_2_nodes, tags=deepcopy(way.tags))

        self.__update_relations(
            original_nodes, self.ways[way.id], [self.ways[new_way_id]]
        )

    def __split_way_at_restriction(self, relation_id, way_id):

        relation = self.relations[relation_id]

        way = self.ways[way_id]
        way_nodes = way.nodes

        if all(relation.via.id != node for node in [way_nodes[0], way_nodes[-1]]):
            self.__split_way(way, relation.via.id)

    def __create_one_directional_ways(self, paths, used_ids, mask_edges, way):
        ways = []
        for path in paths:
            oneway_nodes = self.__edges_to_set(path, mask_edges)

            # If it comes empty it means edges are in opposite direction
            if len(oneway_nodes) == 0:
                inverted_edges = self.__invert_edges(path)
                oneway_nodes = self.__edges_to_set(inverted_edges, mask_edges)

            new_way_tags = deepcopy(way.tags)
            new_way_tags["oneway"] = "yes"
            new_way_id = max([*list(self.ways.keys()), *used_ids]) + 1
            used_ids.append(new_way_id)

            new_way = Way(new_way_id, oneway_nodes.items, new_way_tags)

            ways.append(new_way)

        return ways

    def __create_bi_directional_ways(self, paths, used_ids, mask_edges, way):
        ways = []
        for i, path in enumerate(paths):
            twoway_nodes = self.__edges_to_set(path, mask_edges)
            if i == 0:
                new_way = way
                new_way.nodes = twoway_nodes.items
            else:
                new_way_tags = deepcopy(way.tags)
                new_way_id = max([*list(self.ways.keys()), *used_ids]) + 1
                used_ids.append(new_way_id)

                new_way = Way(new_way_id, twoway_nodes.items, new_way_tags)

            ways.append(new_way)

        return ways

    @staticmethod
    def __get_updated_way_id(
        relation_via_id, node_id, original_way, new_ways, original_nodes, is_via_way
    ):
        if is_via_way:
            relation_nodes = [
                node_id,
                find_common_node(original_nodes, relation_via_id),
            ]
        else:
            relation_nodes = [node_id, relation_via_id]

        if not all([node in relation_nodes for node in original_way.nodes]):
            for new_way in new_ways:
                if all([node in relation_nodes for node in new_way.nodes]):
                    return new_way.id

    @staticmethod
    def __update_via_way(relation, original_way, new_ways):
        if any(way == original_way.id for way in relation.via.ways):
            via_ways = relation.via.ways
            via_ways.extend([way.id for way in new_ways])
            relation.via = ViaWays(relation.via.id, via_ways)

    def __handle_non_matching_directions(
        self, edges, reversed_edges, reversed_reversed_edges, way, mask_edges
    ):
        assert len(edges) != 0 or len(reversed_reversed_edges) != 0

        if len(edges) == 0:
            way.tags["oneway"] = "yes"
            nodes = self.__edges_to_set(reversed_edges, mask_edges)
            way.nodes = nodes.items

        elif len(reversed_reversed_edges) == 0:
            way.tags["oneway"] = "yes"
            nodes = self.__edges_to_set(edges, mask_edges)
            way.nodes = nodes.items
        else:
            original_nodes = deepcopy(way.nodes)

            common_edges = edges.intersection(reversed_reversed_edges)
            different_edges = edges.symmetric_difference(reversed_reversed_edges)

            ways = []
            used_ids = []

            bi_directional_paths = self.__split_paths(common_edges)
            ways.extend(
                self.__create_bi_directional_ways(
                    bi_directional_paths, used_ids, mask_edges, way
                )
            )

            one_directional_paths = self.__split_paths(different_edges)
            ways.extend(
                self.__create_one_directional_ways(
                    one_directional_paths, used_ids, mask_edges, way
                )
            )

            self.__update_relations(
                original_nodes, way, [w for w in ways if w.id != way.id]
            )

            return ways
        return [way]

    def _find_restrictions(self):

        """
        - Check all nodes in each way to see if they connect to any other node not present on that way.
        - Find all ways that intersect and save them as a possible relation (turn).
        """
        for way_id, way in self.ways.items():
            self._find_restriction(way.nodes, way_id)
            self._find_restriction(list(reversed(way.nodes)), way_id)

    def _find_restriction(self, nodes, from_way):
        for i, node in enumerate(nodes):

            # If it's starting point, only coming from opposite direction it could have a restriction
            if i == 0:
                continue

            neighbours = {edge[1] for edge in self.mask.edges if edge[0] == node}

            for neighbour in neighbours:
                if neighbour not in nodes:
                    from_node = nodes[i - 1]
                    to_node = neighbour
                    seq = (from_node, node, to_node)

                    if (
                        seq in self.mask.relations
                        or any(node_id not in self.mask.nodes for node_id in seq)
                        or any(edge not in self.mask.edges for edge in pairwise(seq))
                    ):
                        continue

                    to_way = None
                    for possible_way in self.nodes[neighbour].ways:
                        if all(
                            n in self.ways[possible_way].nodes
                            for n in [node, neighbour]
                        ):
                            to_way = possible_way

                    if to_way:
                        if self.relations.get(seq):
                            self.relations[seq].from_node = from_node
                            self.relations[seq].to_node = to_node
                        else:

                            relation_ids = {
                                relation.id
                                for key, relation in self.relations.items()
                                if relation.id
                            }

                            tags = {
                                "type": "restriction",
                                "restriction": self.__add_relation_metadata(seq),
                                "version": 1,
                            }

                            self.relations[seq] = Relation(
                                id=max(relation_ids) + 1 if relation_ids else 0,
                                from_way=from_way,
                                from_node=from_node,
                                to_way=to_way,
                                to_node=to_node,
                                via=ViaNode(node),
                                tags=tags,
                            )

    def __add_relation_metadata(self, seq):

        edge_1, edge_2 = pairwise(seq)

        nodes_edge_1 = [self.nodes[node] for node in edge_1]
        nodes_edge_2 = [self.nodes[node] for node in edge_2]

        vector_1 = create_vector(nodes_edge_1)
        vector_2 = create_vector(nodes_edge_2)

        # TODO: Handle u-turns and straight_on
        return calculate_direction(vector_1, vector_2)

    def __is_relation_valid(self, via_node_id, way_id, node_id):

        way = self.ways.get(way_id, None)
        if way is None:
            return False

        way_nodes = way.nodes
        edges = pairwise(way_nodes)
        edges.extend(pairwise(list(reversed(way_nodes))))

        if any(
            relation_edge in edges
            for relation_edge in [(via_node_id, node_id), (node_id, via_node_id)]
        ):
            return True

        return False

    def __update_relations(self, original_nodes, original_way, new_ways):
        for rel_id, relation in self.relations.items():

            is_via_way = isinstance(relation.via, ViaWays)

            if relation.from_way == original_way.id:
                new_way_id = self.__get_updated_way_id(
                    relation.via.id,
                    relation.from_node,
                    original_way,
                    new_ways,
                    original_nodes,
                    is_via_way,
                )

                if new_way_id:
                    relation.from_way = new_way_id

            if relation.to_way == original_way.id:
                new_way_id = self.__get_updated_way_id(
                    relation.via.id,
                    relation.to_node,
                    original_way,
                    new_ways,
                    original_nodes,
                    is_via_way,
                )

                if new_way_id:
                    relation.to_way = new_way_id

            if is_via_way:
                self.__update_via_way(relation, original_way, new_ways)
