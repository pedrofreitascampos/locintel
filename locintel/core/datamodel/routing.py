from dataclasses import dataclass
from numbers import Number
from typing import Sequence

from das.routing.core.datamodel.geo import GeoCoordinate, Geometry

WAYPOINT_KINDS = [
    "STOP",  # A stop is expected, next leg may start in any direction
    "VIA",  # Indicative of path to follow, no stops expected, must continue in direction of arrival to waypoint
]

SNAP_POLICIES = [
    "NEAREST",  # Point is matched to nearest navigable road
    "FUZZY",  # Point is matched according to most likely road given rest of route
]

VEHICLE_TYPES = ["CAR", "PEDESTRIAN", "BIKE"]

STRATEGIES = ["FASTEST", "SHORTEST", "ECONOMIC"]


@dataclass
class Waypoint(GeoCoordinate):
    def __init__(self, lat, lng, alt=None, kind="STOP", snap="NEAREST"):
        super(GeoCoordinate, self).__init__()
        self.lat = lat
        self.lng = lng
        self.alt = alt
        self.kind = kind
        self.snap = snap

    def __repr__(self):
        return super().__repr__()

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, k):
        if k not in WAYPOINT_KINDS:
            raise ValueError(
                f"{k} is an unknown waypoint kind, please choose from: {WAYPOINT_KINDS}"
            )
        self._kind = k

    @property
    def snap(self):
        return self._snap

    @snap.setter
    def snap(self, s):
        if s not in SNAP_POLICIES:
            raise ValueError(
                f"{s} is an unknown snap policy, please choose from: {SNAP_POLICIES}"
            )
        self._snap = s

    @classmethod
    def from_geocoordinate(cls, coord, kind="STOP", snap="NEAREST"):
        return cls(coord.lat, coord.lng, coord.alt, kind, snap)

    def to_geocoordinate(self):
        return GeoCoordinate(self.lat, self.lng, self.alt)


@dataclass
class RoutePlan(object):
    def __init__(
        self,
        start: Waypoint,
        end: Waypoint,
        intermediate_waypoints: Sequence[Waypoint] = None,
        vehicle="CAR",
        strategy="FASTEST",
        metadata=None,
    ):
        self.start = start
        self.end = end
        self.intermediate_waypoints = intermediate_waypoints or []
        self.vehicle = vehicle
        self.strategy = strategy
        self.metadata = metadata or {}

    def __repr__(self):
        return f"RoutePlan(start={self.start},end={self.end},metadata={self.metadata})"

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, s):
        if not isinstance(s, Waypoint):
            raise TypeError(f"{s} is not a valid Waypoint type")
        elif s.kind != "STOP":
            raise ValueError(
                f"Waypoint is of kind {s.kind}, but need STOP waypoint for start point"
            )
        self._start = s

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, e):
        if not isinstance(e, Waypoint):
            raise TypeError(f"{e} is not a valid Waypoint type")
        elif e.kind != "STOP":
            raise ValueError(
                f"Waypoint is of kind {e.kind}, but need STOP waypoint for end point"
            )
        self._end = e

    @property
    def intermediate_waypoints(self):
        return self._intermediate_waypoints

    @intermediate_waypoints.setter
    def intermediate_waypoints(self, iws):
        for i, iw in enumerate(iws):
            if not isinstance(iw, Waypoint):
                raise TypeError(
                    f"{iw} (intermediate waypoint #{i}) is not a valid Waypoint type"
                )
        self._intermediate_waypoints = iws

    @property
    def vehicle(self):
        return self._vehicle

    @vehicle.setter
    def vehicle(self, v):
        if v not in VEHICLE_TYPES:
            raise ValueError(
                f"{v} not a valid vehicle type, choose from {VEHICLE_TYPES}"
            )
        self._vehicle = v

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, s):
        if s not in STRATEGIES:
            raise ValueError(f"{s} not a valid strategy, choose from {STRATEGIES}")
        self._strategy = s

    def get_waypoints(self):
        return tuple([self.start] + self.intermediate_waypoints + [self.end])

    @classmethod
    def from_database_document(cls, doc):
        """
        Loads route from database document schema:
            - See https://gitlab.mobilityservices.io/am/roam/routing-python/blob/develop/quality/das/routing/qualitys/schema/route_input.schema

        :param doc: json/database document
        """
        waypoints = doc["waypoints"]
        name = doc["name"]
        start = waypoints[0]
        end = waypoints[-1]
        return cls(
            start=Waypoint(start[1], start[0]),
            end=Waypoint(end[1], end[0]),
            intermediate_waypoints=[
                Waypoint(waypoint[1], waypoint[0]) for waypoint in waypoints[1:-1]
            ],
            metadata={"name": name},
        )

    def to_database_document(self):
        return {"name": self.metadata["name"], "waypoints": self.get_waypoints()}


@dataclass
class Route(object):
    def __init__(
        self, geometry, distance, duration, segments=None, maneuvers=None, metadata=None
    ):
        """
        :param geometry: geometry of the route, as das.routing.core.datamodel.geo.Geometry object
        :param distance: length of the route, in meters
        :param duration: duration of the route, in seconds
        :param segments: map segments traversed by the route, in Jurbey representation, as Segment objects
        :param maneuvers: generated maneuvers for turn-by-turn navigation, as Maneuever objects
        :param metadata: additional metadata for the route (e.g. calculation time, environment, calculation context)
        """
        self.geometry = geometry
        self.distance = distance
        self.duration = duration
        self.segments = segments or []
        self.maneuvers = maneuvers or []
        self.metadata = metadata or {}

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, g):
        if not isinstance(g, Geometry):
            raise TypeError(f"{g} not of Geometry type")
        self._geometry = g

    @property
    def distance(self):
        return self._length

    @distance.setter
    def distance(self, l):
        if not isinstance(l, Number):
            raise TypeError(f"{l} not a number")
        elif l < 0:
            raise ValueError(f"{l} < 0, distance must be non-negative")
        self._length = l

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, d):
        if not isinstance(d, Number):
            raise TypeError(f"{d} not a number")
        elif d < 0:
            raise ValueError(f"{d} < 0, duration must be non-negative")
        self._duration = d

    def __repr__(self):
        return f"Route=({self.geometry})"

    @classmethod
    def from_database_document(cls, doc):
        """
        Convenience method to load route from database document schema:
        - See https://gitlab.mobilityservices.io/am/roam/routing-python/blob/develop/quality/das/routing/quality/schema/route.schema

        :param doc: json/database document
        """
        return cls(
            geometry=Geometry.from_lng_lat_tuples(doc["geometry"]),
            distance=doc["distance"],
            duration=doc["duration"],
            metadata={
                "name": doc["name"],
                "date": doc["date"],
                "calc_time": doc["calcTime"],
                "provider": doc["provider"],
                "route_plan": RoutePlan.from_database_document(doc["routePlan"]),
                "test_run": doc["testRun"],
            },
        )

    def to_database_document(self):
        """
        Serializes route to database document schema:
        - See https://gitlab.mobilityservices.io/am/roam/routing-python/blob/develop/quality/das/routing/quality/schema/route.schema

        :param doc: json/database document
        """
        return {
            "name": self.metadata["name"],
            "date": self.metadata["date"],
            "duration": self.duration,
            "distance": self.distance,
            "calcTime": self.metadata["calc_time"],
            "geometry": self.geometry.to_lng_lat_tuples(),
            "provider": self.metadata["provider"],
            "routePlan": self.metadata["route_plan"].to_database_document(),
            "testRun": self.metadata["test_run"],
        }
