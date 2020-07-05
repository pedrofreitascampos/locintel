"""
Produce random route plans according to criteria
"""
import random

from shapely.geometry import Polygon

from locintel.core.datamodel.routing import RoutePlan, Waypoint

polygons = {
    "berlin": Polygon(
        [
            (13.281949, 52.542348),
            (13.509650, 52.542348),
            (13.509650, 52.482488),
            (13.281949, 52.482488),
        ]
    )
}


class RoutePlanGenerator(object):
    def __init__(self, name):
        self.name = name

    def generate_route(self, *arg, **kwargs):
        raise NotImplementedError("Please implement subclass method")


class RandomRoutePlanGenerator(RoutePlanGenerator):
    def __init__(self):
        super().__init__("random")

    def generate_route(self, polygon, seed=None, identifier=None, **kwargs):
        if seed:
            random.seed(seed)

        coords = list()
        for _ in range(2):
            lng_min, lng_max = polygon.bounds[0], polygon.bounds[2]
            lng = random.uniform(lng_min, lng_max)

            lat_min, lat_max = polygon.bounds[1], polygon.bounds[3]
            lat = random.uniform(lat_min, lat_max)

            coords.append(Waypoint(lat, lng))

        rp = RoutePlan(*coords, **kwargs)

        if identifier is not None:
            rp.identifier = identifier

        return rp
