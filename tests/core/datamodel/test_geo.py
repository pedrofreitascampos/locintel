import numpy as np
import polyline
import shapely.geometry as sg
import utm

from unittest.mock import mock_open, patch, call

from locintel.core.datamodel.geo import *
from tests.fixtures.geo import *


class TestGeoCoordinate(object):
    def test_valid_coordinates(self):
        latitude = 42.0
        longitude = 41.0

        result = GeoCoordinate(lat=latitude, lng=longitude)

        assert isinstance(result, GeoCoordinate)
        assert result.lat == latitude
        assert result.lng == longitude

    def test_valid_coordinates_as_ints(self):
        latitude = 42
        longitude = 41

        result = GeoCoordinate(lat=latitude, lng=longitude)

        assert result.lat == latitude
        assert result.lng == longitude

    def test_invalid_latitude_raises_value_error(self):
        latitudes = [-90.1, 90.1]
        longitude = 41.0

        for latitude in latitudes:
            with pytest.raises(ValueError):
                GeoCoordinate(lat=latitude, lng=longitude)

    def test_invalid_latitude_from_assignment_raises_value_error(self):
        latitude = 42.0
        longitude = 41.0

        coord = GeoCoordinate(lat=latitude, lng=longitude)

        with pytest.raises(ValueError):
            coord.lat = 90.1  # invalid latitude, setter will protect from this

    def test_invalid_type_latitude_raises_type_error(self):
        latitude = "invalid_type"
        longitude = 41.0

        with pytest.raises(TypeError):
            GeoCoordinate(lat=latitude, lng=longitude)

    def test_invalid_longitude_raises_value_error(self):
        latitude = 42.0
        longitudes = [-180.1, 180.1]

        for longitude in longitudes:
            with pytest.raises(ValueError):
                GeoCoordinate(lat=latitude, lng=longitude)

    def test_invalid_longitude_from_assignment_raises_value_error(self):
        latitude = 42.0
        longitude = 41.0

        coord = GeoCoordinate(lat=latitude, lng=longitude)

        with pytest.raises(ValueError):
            coord.lng = 180.1  # invalid longitude, setter will protect from this

    def test_invalid_type_longitude_raises_type_error(self):
        latitude = 41.0
        longitude = "invalid_type"

        with pytest.raises(TypeError):
            GeoCoordinate(lat=latitude, lng=longitude)

    def test_addition(self):
        coord_1 = GeoCoordinate(10, 20)
        coord_2 = GeoCoordinate(5, 7)

        result = coord_1 + coord_2

        assert isinstance(result, GeoCoordinate)
        assert result.lat == 15
        assert result.lng == 27

    def test_is_hashable(self):
        coord = GeoCoordinate(10, 20)

        result = hash(coord)

        assert result == hash(coord.__repr__())

    def test_distance_to(self, mocker):
        coord_1 = GeoCoordinate(10, 20)
        coord_2 = GeoCoordinate(11, 21)
        distance = 50
        shapely_mock_1 = Mock(sg.Point, distance=Mock(return_value=distance))
        shapely_mock_2 = Mock(sg.Point)
        mocker.patch(
            "locintel.core.datamodel.geo.GeoCoordinate.to_shapely_point",
            side_effect=[shapely_mock_1, shapely_mock_2],
        )
        result = coord_1.distance_to(coord_2)

        coord_1.to_shapely_point.assert_called_with(convert_to_utm=True)
        coord_2.to_shapely_point.assert_called_with(convert_to_utm=True)
        shapely_mock_1.distance.assert_called_with(shapely_mock_2)
        assert result == distance

    def test_distance_to_invalid_type_raises_attribute_error(self):
        coord_1 = GeoCoordinate(10, 20)
        coord_2 = "INVALID"
        with pytest.raises(AttributeError):
            coord_1.distance_to(coord_2)

    def test_add_offset(self, mocker):
        coord = GeoCoordinate(10, 20)
        lat_offset, lng_offset = 100, 100
        shapely_mock = Mock(
            sg.Point, x=coord.lng, y=coord.lat, metadata={"utm_zone": 1, "utm_band": 2}
        )
        geocoord_mock = Mock(GeoCoordinate, lat=110, lng=120)
        mocker.patch(
            "locintel.core.datamodel.geo.GeoCoordinate.to_shapely_point",
            return_value=shapely_mock,
        )
        mocker.patch(
            "locintel.core.datamodel.geo.GeoCoordinate.from_shapely_point",
            return_value=geocoord_mock,
        )
        new_shapely_mock = Mock(sg.Point)
        mocker.patch("shapely.geometry.Point", return_value=new_shapely_mock)

        result = coord.add_offset(lat_offset, lng_offset)

        assert isinstance(result, GeoCoordinate)
        assert result == geocoord_mock
        assert result.lat == 110
        assert result.lng == 120
        assert new_shapely_mock.metadata == shapely_mock.metadata
        coord.to_shapely_point.assert_called_with(convert_to_utm=True)
        sg.Point.assert_called_with(coord.lng + lng_offset, coord.lat + lat_offset)
        GeoCoordinate.from_shapely_point.assert_called_with(
            new_shapely_mock, convert_from_utm=True
        )

    def test_add_offset_invalid_type_raises_type_error(self):
        coord = GeoCoordinate(10, 20)
        lat_offset, lng_offset = 100, "INVALID"

        with pytest.raises(TypeError):
            coord.add_offset(lat_offset, lng_offset)

    def test_to_shapely_point(self, mocker):
        coord = GeoCoordinate(10, 20)
        shapely_mock = Mock(sg.Point, x=coord.lng, y=coord.lat)
        mocker.patch("shapely.geometry.Point", return_value=shapely_mock)

        result = coord.to_shapely_point()

        sg.Point.assert_called_with(coord.lng, coord.lat)
        assert result == shapely_mock
        assert result.x == coord.lng
        assert result.y == coord.lat
        assert result.metadata == {}

    def test_to_shapely_point_convert_to_utm(self, mocker):
        coord = GeoCoordinate(10, 20)
        utm_lng, utm_lat, utm_zone, utm_band = 1, 2, "zone", "band"
        shapely_mock = Mock(
            sg.Point,
            x=utm_lng,
            y=utm_lat,
            metadata={"utm_zone": utm_zone, "utm_band": utm_band},
        )
        mocker.patch(
            "utm.from_latlon", return_value=(utm_lng, utm_lat, utm_zone, utm_band)
        )
        mocker.patch("shapely.geometry.Point", return_value=shapely_mock)

        result = coord.to_shapely_point(convert_to_utm=True)

        assert result == shapely_mock
        assert result.x == utm_lng
        assert result.y == utm_lat
        assert result.metadata == {"utm_zone": utm_zone, "utm_band": utm_band}
        sg.Point.assert_called_with(utm_lng, utm_lat)
        utm.from_latlon.assert_called_with(coord.lat, coord.lng)

    def test_from_shapely_point(self):
        shapely_mock = Mock(sg.Point)
        shapely_mock.x = 10
        shapely_mock.y = 20

        result = GeoCoordinate.from_shapely_point(shapely_mock)

        assert isinstance(result, GeoCoordinate)
        assert result.lat == shapely_mock.y
        assert result.lng == shapely_mock.x

    def test_from_shapely_point_convert_from_utm(self, mocker):
        shapely_mock = Mock(
            sg.Point, x=10, y=20, metadata={"utm_band": "band", "utm_zone": "zone"}
        )
        wgs_lng, wgs_lat = 1, 2
        mocker.patch("utm.to_latlon", return_value=(wgs_lat, wgs_lng))

        result = GeoCoordinate.from_shapely_point(shapely_mock, convert_from_utm=True)

        assert isinstance(result, GeoCoordinate)
        assert result.lat == wgs_lat
        assert result.lng == wgs_lng
        utm.to_latlon.assert_called_with(
            shapely_mock.x,
            shapely_mock.y,
            shapely_mock.metadata["utm_zone"],
            shapely_mock.metadata["utm_band"],
        )

    def test_from_shapely_point_convert_from_utm_missing_metadata_raises_value_error(
        self
    ):
        shapely_mock = Mock(sg.Point, x=10, y=20)

        with pytest.raises(ValueError):
            GeoCoordinate.from_shapely_point(shapely_mock, convert_from_utm=True)


class TestGeometry(object):
    def test_geometry_valid_geocoordinates(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        result = Geometry([coord_1, coord_2])

        assert isinstance(result, Geometry)
        assert result.coords[0] == coord_1
        assert result.coords[1] == coord_2

    def test_invalid_geocoordinates_type_raises_type_error(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        coord_1 = "invalid_type"

        with pytest.raises(TypeError):
            Geometry([coord_1, coord_2])

    def test_less_than_two_geocoordinates_raises_value_error(self):
        with pytest.raises(ValueError):
            Geometry([Mock(GeoCoordinate)])

        with pytest.raises(ValueError):
            Geometry([])

    def test_non_sequence_input_raises_value_error(self):
        with pytest.raises(TypeError):
            Geometry(Mock(GeoCoordinate))

    def test_acts_as_iterator(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        geometry = Geometry([coord_1, coord_2])

        result = list(geometry)

        assert result == [coord_1, coord_2]

    def test_get_item_gets_coords(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates

        geometry = Geometry([coord_1, coord_2])

        assert geometry[0] == coord_1
        assert geometry[1] == coord_2

    def test_len_returns_coordinates_length(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates

        geometry = Geometry([coord_1, coord_2, coord_1])

        assert len(geometry) == 3

    def test_equality_by_coordinates(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        geo_1 = Geometry([coord_1, coord_2])
        geo_1.metadata = "metadata_1"
        geo_2 = Geometry([coord_1, coord_2])
        geo_2.metadata = "metadata_2"
        assert geo_1 == geo_2

    def test_length(self, mocker, test_geometry):
        geometry = test_geometry
        length = 10
        linestring_mock = Mock(sg.LineString, length=length)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.to_linestring",
            return_value=linestring_mock,
        )

        result = geometry.length()

        assert result == length
        geometry.to_linestring.assert_called_with(convert_to_utm=True)

    def test_center_of_mass(self):
        result = Geometry(
            [GeoCoordinate(-1.0, -1.0), GeoCoordinate(1.0, 1.0)]
        ).center_of_mass()
        assert result.lat == 0.0
        assert result.lng == 0.0

    def test_skewness(self, mocker):
        coord_1 = GeoCoordinate(10, 20)
        coord_2 = GeoCoordinate(11, 21)
        straight_line_distance = 50
        shapely_mock_1 = Mock(
            sg.Point, distance=Mock(return_value=straight_line_distance)
        )
        shapely_mock_2 = Mock(sg.Point)
        mocker.patch(
            "locintel.core.datamodel.geo.GeoCoordinate.to_shapely_point",
            side_effect=[shapely_mock_1, shapely_mock_2],
        )
        length = 100
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.length", return_value=length
        )

        geometry = Geometry([coord_1, coord_2])
        result = geometry.skewness()

        coord_1.to_shapely_point.assert_called_with(convert_to_utm=True)
        coord_2.to_shapely_point.assert_called_with(convert_to_utm=True)
        shapely_mock_1.distance.assert_called_with(shapely_mock_2)
        assert result == 2  # length / straight line distance

    def test_skewness_zero_length(self):
        coord = GeoCoordinate(10, 20)
        geometry = Geometry([coord, coord])

        with pytest.raises(ZeroDivisionError):
            geometry.skewness()

    def test_has_loops_returns_false_when_no_repeated_points(self, test_geometry):
        geometry = test_geometry

        result = geometry.has_loops()

        assert result is False

    def test_has_loops_returns_true_when_there_are_repeated_points(
        self, mock_geocoordinates
    ):
        coord_1, coord_2 = mock_geocoordinates
        geometry = Geometry([coord_1, coord_2, coord_1])

        result = geometry.has_loops()

        assert result is True

    def test_has_loops_returns_false_when_route_length_zero(self, mock_geocoordinates):
        coord_1, _ = mock_geocoordinates
        geometry = Geometry([coord_1, coord_1])

        result = geometry.has_loops()

        assert result is False

    def test_is_irregular_returns_true_when_route_has_loops(
        self, mocker, test_geometry
    ):
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.skewness", return_value=10
        )
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.has_loops", return_value=True
        )
        geometry = test_geometry

        result = geometry.is_irregular()

        assert result is True

    def test_is_irregular_returns_true_when_route_is_too_skewed(
        self, mocker, test_geometry
    ):
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.skewness", return_value=10
        )
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.has_loops", return_value=False
        )
        geometry = test_geometry

        result = geometry.is_irregular(skew_threshold=9)

        assert result is True

    def test_is_irregular_returns_true_when_route_is_too_skewed_and_has_loops(
        self, mocker, test_geometry
    ):
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.skewness", return_value=10
        )
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.has_loops", return_value=True
        )
        geometry = test_geometry

        result = geometry.is_irregular(skew_threshold=9)

        assert result is True

    def test_is_irregular_returns_false_when_route_is_neither_skewed_nor_has_no_loops(
        self, mocker, test_geometry
    ):
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.skewness", return_value=10
        )
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.has_loops", return_value=False
        )
        geometry = test_geometry

        result = geometry.is_irregular(skew_threshold=15)

        assert result is False

    def test_shift(self):
        shifted_coord_1 = Mock(GeoCoordinate, lat=20, lng=40)
        shifted_coord_2 = Mock(GeoCoordinate, lat=40, lng=60)
        coord_1 = Mock(
            GeoCoordinate, lat=10, lng=30, add_offset=Mock(return_value=shifted_coord_1)
        )
        coord_2 = Mock(
            GeoCoordinate, lat=30, lng=50, add_offset=Mock(return_value=shifted_coord_2)
        )
        lat_shift = 10
        lng_shift = 20

        geometry = Geometry([coord_1, coord_2])
        result = geometry.shift(lat_shift, lng_shift)

        assert isinstance(result, Geometry)
        assert result[0].lat == shifted_coord_1.lat
        assert result[0].lng == shifted_coord_1.lng
        assert result[1].lat == shifted_coord_2.lat
        assert result[1].lng == shifted_coord_2.lng
        coord_1.add_offset.assert_called_with(lat_shift, lng_shift)
        coord_2.add_offset.assert_called_with(lat_shift, lng_shift)

    def test_add_noise(self, mocker):
        # random noise mocking
        lat_offset_1 = 2
        lng_offset_1 = 3.1
        lat_offset_2 = 1
        lng_offset_2 = 2.4
        mocker.patch(
            "numpy.random.normal",
            side_effect=[lat_offset_1, lng_offset_1, lat_offset_2, lng_offset_2],
        )
        shifted_coord_1 = Mock(GeoCoordinate, lat=12, lng=33.1)
        shifted_coord_2 = Mock(GeoCoordinate, lat=31, lng=52.4)
        coord_1 = Mock(
            GeoCoordinate, lat=10, lng=30, add_offset=Mock(return_value=shifted_coord_1)
        )
        coord_2 = Mock(
            GeoCoordinate, lat=30, lng=50, add_offset=Mock(return_value=shifted_coord_2)
        )

        geometry = Geometry([coord_1, coord_2])
        result = geometry.add_noise()

        assert isinstance(result, Geometry)
        assert result[0].lat == shifted_coord_1.lat
        assert result[0].lng == shifted_coord_1.lng
        assert result[1].lat == shifted_coord_2.lat
        assert result[1].lng == shifted_coord_2.lng
        np.random.normal.assert_has_calls([call(loc=0, scale=4.2)] * 4)
        coord_1.add_offset.assert_called_with(lat_offset_1, lng_offset_1)
        coord_2.add_offset.assert_called_with(lat_offset_2, lng_offset_2)

    def test_add_noise_accepts_seed(self):
        # kind of integration test, making sure we freeze numpy.random's seed when required
        shifted_coord_1 = Mock(GeoCoordinate, lat=12, lng=33.1)
        shifted_coord_2 = Mock(GeoCoordinate, lat=31, lng=52.4)
        coord_1 = Mock(
            GeoCoordinate, lat=10, lng=30, add_offset=Mock(return_value=shifted_coord_1)
        )
        coord_2 = Mock(
            GeoCoordinate, lat=30, lng=50, add_offset=Mock(return_value=shifted_coord_2)
        )
        # seed and np.random offsets for seed
        seed = 2
        lat_offset_1, lng_offset_1 = -1.7503829591029767, -0.2363206743505838
        lat_offset_2, lng_offset_2 = -8.972023601807507, 6.889137395300953

        geometry = Geometry([coord_1, coord_2])
        result = geometry.add_noise(seed=seed)

        assert isinstance(result, Geometry)
        coord_1.add_offset.assert_called_with(lat_offset_1, lng_offset_1)
        coord_2.add_offset.assert_called_with(lat_offset_2, lng_offset_2)

    def test_add_noise_specify_kwargs(self, mocker):
        # random noise mocking
        lat_offset_1 = 2
        lng_offset_1 = 3.1
        lat_offset_2 = 1
        lng_offset_2 = 2.4
        mocker.patch(
            "numpy.random.normal",
            side_effect=[lat_offset_1, lng_offset_1, lat_offset_2, lng_offset_2],
        )
        shifted_coord_1 = Mock(GeoCoordinate, lat=12, lng=33.1)
        shifted_coord_2 = Mock(GeoCoordinate, lat=31, lng=52.4)
        coord_1 = Mock(
            GeoCoordinate, lat=10, lng=30, add_offset=Mock(return_value=shifted_coord_1)
        )
        coord_2 = Mock(
            GeoCoordinate, lat=30, lng=50, add_offset=Mock(return_value=shifted_coord_2)
        )
        loc = 2
        scale = 5

        geometry = Geometry([coord_1, coord_2])
        result = geometry.add_noise(loc=loc, scale=scale)

        assert isinstance(result, Geometry)
        assert result[0].lat == shifted_coord_1.lat
        assert result[0].lng == shifted_coord_1.lng
        assert result[1].lat == shifted_coord_2.lat
        assert result[1].lng == shifted_coord_2.lng
        np.random.normal.assert_has_calls([call(loc=loc, scale=scale)] * 4)
        coord_1.add_offset.assert_called_with(lat_offset_1, lng_offset_1)
        coord_2.add_offset.assert_called_with(lat_offset_2, lng_offset_2)

    def test_add_noise_specify_function(self, mocker):
        # return same coord by passing lambda x: x as func
        coord_1 = Mock(GeoCoordinate, lat=10, lng=30)
        coord_1.add_offset = Mock(return_value=coord_1)
        coord_2 = Mock(GeoCoordinate, lat=30, lng=50)
        coord_2.add_offset = Mock(return_value=coord_2)
        kwargs = {"offset": 0}
        mocker.patch("numpy.random.normal")

        geometry = Geometry([coord_1, coord_2])
        result = geometry.add_noise(func=lambda offset: offset, **kwargs)

        assert isinstance(result, Geometry)
        assert result[0].lat == coord_1.lat
        assert result[0].lng == coord_1.lng
        assert result[1].lat == coord_2.lat
        assert result[1].lng == coord_2.lng
        np.random.normal.assert_not_called()
        coord_1.add_offset.assert_called_with(0, 0)
        coord_2.add_offset.assert_called_with(0, 0)

    def test_subsample(self):
        geometry = Geometry([Mock(GeoCoordinate)] * 100)
        period = 5

        result = geometry.subsample(period=period)

        assert isinstance(result, Geometry)
        assert len(result) == len(geometry) / period

    def test_subsample_includes_start_point(self):
        geometry = Geometry([Mock(GeoCoordinate)] * 99)

        result = geometry.subsample()

        assert isinstance(result, Geometry)
        assert result[0] == geometry[0]

    def test_subsample_includes_end_point(self):
        geometry = Geometry([Mock(GeoCoordinate)] * 98)
        geometry.coords[-1] = Mock(GeoCoordinate, lat=10, lng=20)
        period = 50

        result = geometry.subsample(period=period)

        assert isinstance(result, Geometry)
        assert result[-1] == geometry[-1]
        assert len(result) == 3  # start, middle, end

    def test_subsample_two_point_returns_same_geometry(self):
        geometry = Geometry([Mock(GeoCoordinate)] * 2)
        period = 10

        result = geometry.subsample(period=period)

        assert isinstance(result, Geometry)
        assert result == geometry

    def test_dummy(self):
        result = Geometry.dummy()

        assert isinstance(result, Geometry)

    def test_from_polyline(self, mocker, mock_geometry):
        decoded_geometry = mock_geometry
        decoded_polyline = tuple([(p.lat, p.lng) for p in decoded_geometry.coords])
        polyline_str = "polyline"
        mocker.patch("polyline.decode", return_value=decoded_polyline)

        result = Geometry.from_polyline(polyline_str)

        polyline.decode.assert_called_with(polyline_str)
        assert result.coords[0].lat == decoded_geometry.coords[0].lat
        assert result.coords[0].lng == decoded_geometry.coords[0].lng
        assert result.coords[1].lat == decoded_geometry.coords[1].lat
        assert result.coords[1].lng == decoded_geometry.coords[1].lng

    def test_from_geojson(self, mocker, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        coordinates = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]
        mocker.patch("geojson.load", return_value={"coordinates": coordinates})
        target_geometry = Mock(Geometry)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_lng_lat_tuples",
            return_value=target_geometry,
        )
        filename = "filename"
        m = mock_open()
        with patch("locintel.core.datamodel.geo.open", m, create=True):
            result = Geometry.from_geojson(filename)

            assert result == target_geometry
            m.assert_called_once_with(filename)
            Geometry.from_lng_lat_tuples.assert_called_with(coordinates)
            # TODO: patch geojson.load, check call to read

    def test_from_geojson_has_geometry(self, mocker, mock_geocoordinates):
        #  Case in which the GeoJSON has a Geometry field
        coord_1, coord_2 = mock_geocoordinates
        coordinates = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]
        mocker.patch(
            "geojson.load", return_value={"geometry": {"coordinates": coordinates}}
        )
        target_geometry = Mock(Geometry)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_lng_lat_tuples",
            return_value=target_geometry,
        )
        filename = "filename"
        m = mock_open()
        with patch("locintel.core.datamodel.geo.open", m, create=True):
            result = Geometry.from_geojson(filename)

            assert result == target_geometry
            m.assert_called_once_with(filename)
            Geometry.from_lng_lat_tuples.assert_called_with(coordinates)
            # TODO: patch geojson.load, check call to read

    def test_from_geojson_has_features(self, mocker, mock_geocoordinates):
        #  Case in which GeoJSON has features field
        coord_1, coord_2 = mock_geocoordinates
        coordinates = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]
        mocker.patch(
            "geojson.load",
            return_value={"features": [{"geometry": {"coordinates": coordinates}}]},
        )
        target_geometry = Mock(Geometry)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_lng_lat_tuples",
            return_value=target_geometry,
        )
        filename = "filename"
        m = mock_open()
        with patch("locintel.core.datamodel.geo.open", m, create=True):
            result = Geometry.from_geojson(filename)

            assert result == target_geometry
            m.assert_called_once_with(filename)
            Geometry.from_lng_lat_tuples.assert_called_with(coordinates)
            # TODO: patch geojson.load, check call to read

    def test_from_geojson_has_features_choose_feature_index(
        self, mocker, mock_geocoordinates
    ):
        coord_1, coord_2 = mock_geocoordinates
        coordinates = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]
        mocker.patch(
            "geojson.load",
            return_value={
                "features": [
                    {"geometry": {"coordinates": coordinates}},
                    {"geometry": {"coordinates": coordinates[::-1]}},
                ]
            },
        )
        target_geometry = Mock(Geometry)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.from_lng_lat_tuples",
            return_value=target_geometry,
        )
        filename = "filename"
        m = mock_open()
        with patch("locintel.core.datamodel.geo.open", m, create=True):
            result = Geometry.from_geojson(filename, index=1)

            assert result == target_geometry
            m.assert_called_once_with(filename)
            Geometry.from_lng_lat_tuples.assert_called_with(coordinates[::-1])
            # TODO: patch geojson.load, check call to read

    def test_from_lat_lng_dicts(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        lat_lon_dicts = [
            {"lat": coord_1.lat, "lon": coord_1.lng},
            {"lat": coord_2.lat, "lon": coord_2.lng},
        ]

        result = Geometry.from_lat_lon_dicts(lat_lon_dicts)

        assert isinstance(result, Geometry)
        assert result.coords[0].lat == coord_1.lat
        assert result.coords[0].lng == coord_1.lng
        assert result.coords[1].lat == coord_2.lat
        assert result.coords[1].lng == coord_2.lng

    def test_from_lat_lng_tuples(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        lat_lng_tuples = [(coord_1.lat, coord_1.lng), (coord_2.lat, coord_2.lng)]

        result = Geometry.from_lat_lng_tuples(lat_lng_tuples)

        assert isinstance(result, Geometry)
        assert result.coords[0].lat == coord_1.lat
        assert result.coords[0].lng == coord_1.lng
        assert result.coords[1].lat == coord_2.lat
        assert result.coords[1].lng == coord_2.lng

    def test_from_lng_lat_tuples(self, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        lng_lat_tuples = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]

        result = Geometry.from_lng_lat_tuples(lng_lat_tuples)

        assert isinstance(result, Geometry)
        assert result.coords[0].lat == coord_1.lat
        assert result.coords[0].lng == coord_1.lng
        assert result.coords[1].lat == coord_2.lat
        assert result.coords[1].lng == coord_2.lng

    def test_to_polyline(self, mocker, mock_geometry, test_polyline):
        lat_lng_tuple = ((10, 20), (20, 30))
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.to_lat_lng_tuples",
            return_value=lat_lng_tuple,
        )
        mocker.patch("polyline.encode", return_value=test_polyline)

        result = mock_geometry.to_polyline()

        assert result == test_polyline
        Geometry.to_lat_lng_tuples.assert_called_with()
        polyline.encode.assert_called_with(lat_lng_tuple, precision=5)

    def test_to_linestring(self, mocker, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        lng_lat_tuple = [(coord_1.lng, coord_1.lat), (coord_2.lng, coord_2.lat)]
        mock_linestring = Mock(sg.LineString)
        mocker.patch("shapely.geometry.LineString", return_value=mock_linestring)
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.to_lng_lat_tuples",
            return_value=lng_lat_tuple,
        )
        geometry = Geometry([coord_1, coord_2])

        result = geometry.to_linestring()

        assert isinstance(result, sg.linestring.LineString)
        assert result == mock_linestring
        sg.LineString.assert_called_with(lng_lat_tuple)

    def test_to_linestring_convert_to_utm(self, mocker, mock_geocoordinates):
        coord_1, coord_2 = mock_geocoordinates
        lat_lng_tuple = [
            (coord_1.lat, coord_1.lng),
            (coord_2.lat, coord_2.lng),
            (coord_1.lat, coord_1.lng),
        ]
        mocker.patch(
            "locintel.core.datamodel.geo.Geometry.to_lat_lng_tuples",
            return_value=lat_lng_tuple,
        )
        geometry = Geometry([coord_1, coord_2, coord_1])
        utm_easting_1, utm_northing_1, utm_easting_2, utm_northing_2 = 10, 15, 20, 25
        utm_coord_1 = (utm_easting_1, utm_northing_1, "zone_1", "band_1")
        utm_coord_2 = (utm_easting_2, utm_northing_2, "zone_2", "band_2")
        utm_coord_3 = utm_coord_1
        mocker.patch(
            "utm.from_latlon",
            side_effect=[utm_coord_1[:2], utm_coord_2[:2], utm_coord_3[:2]],
        )
        mock_linestring = Mock(sg.LineString)
        mocker.patch("shapely.geometry.LineString", return_value=mock_linestring)

        result = geometry.to_linestring(convert_to_utm=True)

        assert isinstance(result, sg.linestring.LineString)
        assert result == mock_linestring
        print(lat_lng_tuple[0])
        utm.from_latlon.assert_has_calls(
            [call(*lat_lng_tuple[0]), call(*lat_lng_tuple[1]), call(*lat_lng_tuple[2])]
        )
        sg.LineString.assert_called_with(
            [utm_coord_1[:2], utm_coord_2[:2], utm_coord_3[:2]]
        )

    def test_to_geojson(self, mock_geometry, test_geojson):
        test_geojson["features"].pop()  # remove MultiPoint from fixture
        assert mock_geometry.to_geojson() == test_geojson

    def test_to_geojson_with_points(self, mock_geometry, test_geojson):
        assert mock_geometry.to_geojson(draw_points=True) == test_geojson

    def test_to_geojson_write_to_file(self, mock_geometry):
        filename = "filename"
        m = mock_open()
        with patch("locintel.core.datamodel.geo.open", m, create=True):
            result = mock_geometry.to_geojson(write_to=filename)

        assert result is None
        m.assert_called_once_with(
            filename, "w"
        )  # TODO: patch geojson.dumps, check call to write

    def test_to_lat_lng_tuples(self, mock_geometry, test_coordinates):
        result = mock_geometry.to_lat_lng_tuples()

        lat_1, lng_1, lat_2, lng_2 = test_coordinates
        assert isinstance(result, tuple)
        assert result[0] == (lat_1, lng_1)
        assert result[1] == (lat_2, lng_2)

    def test_to_lng_lat_tuples(self, mock_geometry, test_coordinates):
        result = mock_geometry.to_lng_lat_tuples()

        lat_1, lng_1, lat_2, lng_2 = test_coordinates
        assert isinstance(result, tuple)
        assert result[0] == (lng_1, lat_1)
        assert result[1] == (lng_2, lat_2)
