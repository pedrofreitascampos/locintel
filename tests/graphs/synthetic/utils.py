import numpy as np

from locintel.core.datamodel.geo import GeoCoordinate
from locintel.graphs.datamodel.jurbey import Edge
from locintel.graphs.datamodel.types import (
    EdgeType,
    RoadClass,
    RoadAccessibility,
    VehicleType,
)
from typing import Sequence


def no_geometry(coord1, coord2):
    return {}


def simple_node_geometry(coord1, coord2):
    return [coord1, coord2]


def interpolated_geometry(coord1, coord2):
    new_geometry = np.linspace(
        *[(coord.lat, coord.lng) for coord in (coord1, coord2)], num=5
    )
    return [GeoCoordinate(point[0], point[1]) for point in new_geometry]


def create_edge(**kwargs):
    args = {
        "edge_type": EdgeType.LANE_STRAIGHT,
        "from_node": 0,
        "to_node": 1,
        "road_class": RoadClass.MajorRoad,
        "road_accessibility": RoadAccessibility.NoRestriction,
        "geometry": [],
        "metadata": {"oneway": "yes", "highway": "primary"},
        "vehicle_accessibility": [VehicleType.Car],
    }
    args.update(kwargs)

    return Edge(
        args["edge_type"],
        args["from_node"],
        args["to_node"],
        args["road_class"],
        args["road_accessibility"],
        args["vehicle_accessibility"],
        args["geometry"],
        metadata=args["metadata"],
    )


def requires(requirements):
    def _needs(func):
        def _needs_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        _needs_wrapper.__annotations__ = {
            "requirements": requirements
            if isinstance(requirements, Sequence)
            else [requirements]
        }

        _needs_wrapper.__name__ = func.__name__
        return _needs_wrapper

    return _needs


def find_midpoint(geometry):
    start_coord = geometry[0]
    end_coord = geometry[-1]
    return GeoCoordinate(
        (end_coord.lng + start_coord.lng / 2), (end_coord.lat + start_coord.lat / 2)
    )
