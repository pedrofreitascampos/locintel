from typing import Sequence

from das.routing.core.datamodel.geo import GeoCoordinate


class MatchWaypoint(GeoCoordinate):
    def __init__(self, lat, lng, time=None, bearing=None, radius=None, **kwargs):
        super().__init__(lat, lng)
        self.time = time
        self.bearing = bearing
        self.radius = radius

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_probe(cls, probe, radius=None, **kwargs):
        return cls(
            probe.lat, probe.lng, probe.time, probe.bearing, radius=radius, **kwargs
        )


class MatchPlan(object):
    def __init__(self, points: Sequence[MatchWaypoint], **kwargs):
        self.points = points

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, pts):
        for i, pt in enumerate(pts):
            if not isinstance(pt, MatchWaypoint):
                raise TypeError(f"{pts} (point #{i}) is not a valid MatchWaypoint type")
        self._points = pts

    @classmethod
    def from_trace(cls, trace, radius=None, **kwargs):
        return cls(
            [MatchWaypoint.from_probe(probe, radius=radius) for probe in trace.probes],
            identifier=trace.identifier,
            **kwargs,
        )

    @classmethod
    def from_database_document(cls, doc):
        if doc.get("timestamps"):
            assert len(doc["waypoints"]) == len(doc["timestamps"])
            return cls(
                [
                    MatchWaypoint(waypoint[1], waypoint[0], time=timestamp)
                    for waypoint, timestamp in zip(doc["waypoints"], doc["timestamps"])
                ]
            )
        else:
            return cls(
                [
                    MatchWaypoint(waypoint[1], waypoint[0])
                    for waypoint in doc["waypoints"]
                ],
                identifier=doc.get("id"),
            )

    @classmethod
    def from_route_plan(cls, route_plan, **kwargs):
        return cls(
            [
                MatchWaypoint(point.lat, point.lng, **kwargs)
                for point in route_plan.get_waypoints()
            ]
        )
