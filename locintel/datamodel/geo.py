from dataclasses import dataclass
import geojson
from numbers import Number
import numpy as np
import polyline
import shapely.geometry as sg
from typing import Sequence
import utm


@dataclass
class GeoCoordinate(object):
    lat: float
    lng: float
    alt: float = 0.0

    def __repr__(self):
        return f"GeoCoordinate(lat={self.lat},lng={self.lng})"

    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng and self.alt == other.alt

    def __add__(self, other):
        return GeoCoordinate(self.lat + other.lat, self.lng + other.lng)

    def __hash__(self):
        return hash(repr(self))

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, latitude: Number):
        if not isinstance(latitude, Number):
            raise TypeError(f"{latitude} is not a number")
        if -90 <= latitude <= 90:
            self._lat = latitude
        else:
            raise ValueError(
                f"{latitude} not a valid latitude (must be between -90 and 90)"
            )

    @property
    def lng(self):
        return self._lng

    @lng.setter
    def lng(self, longitude: Number):
        if not isinstance(longitude, Number):
            raise TypeError(f"{longitude} is not a number")
        if -180 <= longitude <= 180:
            self._lng = longitude
        else:
            raise ValueError(
                f"{longitude} not a valid longitude (must be between -180 and 180)"
            )

    def distance_to(self, geocoordinate):
        return self.to_shapely_point(convert_to_utm=True).distance(
            geocoordinate.to_shapely_point(convert_to_utm=True)
        )

    def add_offset(self, lat_offset, lng_offset):
        point = self.to_shapely_point(convert_to_utm=True)
        new_point = sg.Point(point.x + lng_offset, point.y + lat_offset)
        new_point.metadata = point.metadata
        return GeoCoordinate.from_shapely_point(new_point, convert_from_utm=True)

    def to_shapely_point(self, convert_to_utm=False):
        if convert_to_utm:
            lng, lat, zone, band = utm.from_latlon(self.lat, self.lng)
            # this is required to convert back to wgs84 if needed
            metadata = {"utm_zone": zone, "utm_band": band}
        else:
            lat, lng = self.lat, self.lng
            metadata = {}

        point = sg.Point(lng, lat)
        point.metadata = metadata
        return point

    @classmethod
    def from_shapely_point(cls, point, convert_from_utm=False):
        if convert_from_utm:
            try:
                zone = point.metadata["utm_zone"]
                band = point.metadata["utm_band"]
            except (AttributeError, KeyError):
                raise ValueError(
                    "Shapely point requires metadata dict with UTM zone and band when converting from UTM"
                )

            lat, lng = utm.to_latlon(point.x, point.y, zone, band)
        else:
            lat = point.y
            lng = point.x

        return cls(lat, lng)


@dataclass
class Geometry(object):
    def __init__(self, coords: Sequence[GeoCoordinate]):
        self.coords = coords

    def __iter__(self):
        yield from self.coords

    def __getitem__(self, item):
        return self.coords[item]

    def __len__(self):
        return len(self.coords)

    def __eq__(self, other):
        return self.coords == other.coords

    def __add__(self, other):
        self.coords += other.coords

    def __repr__(self):
        return f"Geometry(start={self.coords[0]}...end={self.coords[1]})"

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, coordinates):
        if not isinstance(coordinates, Sequence):
            raise TypeError(f"{coordinates} not a sequence of GeoCoordinate")
        elif len(coordinates) < 2:
            raise ValueError(f"{coordinates} has less than two GeoCoordinate elements")
        for i, coord in enumerate(coordinates):
            if not isinstance(coord, GeoCoordinate):
                raise TypeError(f"{coord} (element #{i}) is not a GeoCoordinate")

        self._coords = coordinates

    def length(self):
        """
        Estimate geometry length, from point interpolation
        """
        return self.to_linestring(convert_to_utm=True).length

    def center_of_mass(self):
        """
        Calculate (naive) center of mass for whole geometry

        Note: since no conversion to UTM is done, this is a naive center of mass, that is, it does not take great circle
              distances into consideration
        """
        return GeoCoordinate.from_shapely_point(self.to_linestring().centroid)

    def skewness(self):
        """
        Estimate skewness of geometry, in relation to straight line distance
        """
        start = self.coords[0].to_shapely_point(convert_to_utm=True)
        end = self.coords[-1].to_shapely_point(convert_to_utm=True)
        straight_line_distance = start.distance(end)
        return self.length() / straight_line_distance

    def has_loops(self):
        """
        Detect loops in route (note: very naive method currently which just looks for repeated points)
        """
        if len(self.coords) == 2:
            return False

        return len(list(set(self.coords))) != len(self.coords)

    def is_irregular(self, skew_threshold=1.8):
        """
        Determine whether geometry looks irregular, or fishy:
            * Currently considers only skewness threshold and presence of loops
        """
        return self.skewness() > skew_threshold or self.has_loops()

    def shift(self, lat_offset, lng_offset):
        """
        Shifts whole geometry by defined lat, lng offsets.

        Requires conversion to UTM to work in meters (more meaningful) and to preserve perspective.

        :param lat_offset: in meters
        :param lng_offset: in meters
        """
        return Geometry(
            [coord.add_offset(lat_offset, lng_offset) for coord in self.coords]
        )

    def add_noise(self, func=None, seed=None, **kwargs):
        """
        Adds "noise" to the geometry points, according to provided function/distribution and respective parameters

        Requires conversion to UTM to work in meters (more meaningful) and to preserve perspective.

        :param func: noise producing function, assumes normal GPS distribution if nothing specified
        :param seed: seed to use for numpy random methods
        :param kwargs: function parameters as kwargs
        """
        # if no kwargs provided assume GPS error
        func = func or np.random.normal
        kwargs = kwargs or {"loc": 0, "scale": 4.2}

        if seed:
            np.random.seed(seed)

        offset_coords = list()
        for coord in self.coords:
            lat_offset = func(**kwargs)
            lng_offset = func(**kwargs)
            offset_coord = coord.add_offset(lat_offset, lng_offset)
            offset_coords.append(offset_coord)

        return Geometry(offset_coords)

    def subsample(self, period=5):
        coords = self.coords[::period]

        if self.coords[0] not in coords or len(self.coords) < 3:
            return Geometry([coords[0], coords[-1]])

        if self.coords[-1] not in coords:
            coords += [self.coords[-1]]

        return Geometry(coords)

    @classmethod
    def dummy(cls):
        # Return dummy Geometry (useful for quick testing)
        return cls(
            [
                GeoCoordinate(52.507485, 13.329857),
                GeoCoordinate(52.506412, 13.332180),
                GeoCoordinate(52.505412, 13.334180),
            ]
        )

    @classmethod
    def from_polyline(cls, polyline_str):
        return cls(
            [
                GeoCoordinate(point[0], point[1])
                for point in polyline.decode(polyline_str)
            ]
        )

    @classmethod
    def from_geojson(cls, filename, index=0):
        json = geojson.load(open(filename))
        try:
            coords = json["coordinates"]
        except KeyError:
            try:
                coords = json["geometry"]["coordinates"]
            except KeyError:
                coords = json["features"][index]["geometry"]["coordinates"]

        return cls.from_lng_lat_tuples(coords)

    @classmethod
    def from_lat_lon_dicts(cls, lat_lon_dicts):
        return cls(
            [GeoCoordinate(coord["lat"], coord["lon"]) for coord in lat_lon_dicts]
        )

    @classmethod
    def from_lat_lng_tuples(cls, lat_lng_tuples):
        return cls([GeoCoordinate(*coord) for coord in lat_lng_tuples])

    @classmethod
    def from_lng_lat_tuples(cls, lng_lat_tuples):
        return cls([GeoCoordinate(*coord[::-1]) for coord in lng_lat_tuples])

    def to_polyline(self, precision=5):
        return polyline.encode(self.to_lat_lng_tuples(), precision=precision)

    def to_linestring(self, convert_to_utm=False):
        if convert_to_utm:
            coords = [utm.from_latlon(*coord)[:2] for coord in self.to_lat_lng_tuples()]
        else:
            coords = self.to_lng_lat_tuples()
        return sg.LineString(coords)

    def to_geojson(
        self,
        draw_points=False,
        write_to=None,
        linestring_props=None,
        multipoint_props=None,
    ):
        geometry = geojson.Feature(
            geometry=geojson.LineString(self.to_lng_lat_tuples()),
            properties=linestring_props,
        )
        features = geojson.FeatureCollection([geometry])

        if draw_points:
            points = geojson.Feature(
                geometry=geojson.MultiPoint([(p.lng, p.lat) for p in self.coords]),
                properties=multipoint_props,
            )
            features = geojson.FeatureCollection([geometry, points])

        if write_to:
            with open(write_to, "w") as f:
                f.write(geojson.dumps(features))
        else:
            return features

    def to_lat_lng_tuples(self):
        return tuple([(p.lat, p.lng) for p in self.coords])

    def to_lng_lat_tuples(self):
        return tuple([(p.lng, p.lat) for p in self.coords])
