from dataclasses import dataclass
from datetime import datetime
from numbers import Number
from typing import Sequence

from das.routing.core.datamodel.geo import GeoCoordinate


@dataclass
class Probe(GeoCoordinate):
    def __init__(self, lat, lng, time, bearing=None, confidence=None):
        super().__init__(lat, lng)
        self.time = time
        self.bearing = bearing
        self.confidence = confidence

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, ts):
        if not isinstance(ts, datetime):
            raise TypeError(f"{ts} wrong type, must be `datetime`")
        self._time = ts

    @property
    def bearing(self):
        return self._bearing

    @bearing.setter
    def bearing(self, b):
        if b is None:
            pass
        elif not isinstance(b, Number):
            raise TypeError(f"{b} wrong type, must be numberical or `None`")
        elif not 0 <= b <= 360:
            raise ValueError(
                f"invalid value for {b}, must be between 0 and 360, inclusive"
            )
        self._bearing = b

    @classmethod
    def from_druid(cls, probe):
        return cls(
            lat=probe["event"]["coordinatelatitude"],
            lng=probe["event"]["coordinatelongitude"],
            time=datetime.fromisoformat(probe["event"]["timestamp"].rstrip("Z")),
        )


class Trace(object):
    def __init__(self, probes: Sequence[Probe], identifier=None):
        self.probes = probes
        self.identifier = identifier or ""

    def __iter__(self):
        return iter(self.probes)

    def __getitem__(self, item):
        return self.probes[item]
