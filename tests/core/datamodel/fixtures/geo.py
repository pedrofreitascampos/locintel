from geojson import FeatureCollection, Feature, LineString, MultiPoint
import pytest
from unittest.mock import Mock

from locintel.core.datamodel.geo import Geometry, GeoCoordinate


@pytest.fixture
def test_coordinates():
    # Coordinates fixture used for the tests
    lat_1, lng_1 = (10.0, 20.0)
    lat_2, lng_2 = (25.0, 30.0)
    return lat_1, lng_1, lat_2, lng_2


@pytest.fixture
def test_polyline():
    # Polyline fixture used for the tests (converted from test_coordinates with precision=5)
    return "polyline"


@pytest.fixture
def test_geojson(test_coordinates):
    # GeoJSON fixture used for the tests (converted from test_coordinates)
    lat_1, lng_1, lat_2, lng_2 = test_coordinates
    coords = [(lng_1, lat_1), (lng_2, lat_2)]
    f1 = Feature(geometry=LineString(coords))
    f2 = Feature(geometry=MultiPoint(coords))
    return FeatureCollection([f1, f2])


@pytest.fixture
def mock_geocoordinates(test_coordinates):
    coord_1, coord_2 = Mock(GeoCoordinate), Mock(GeoCoordinate)
    coord_1.lat, coord_1.lng, coord_2.lat, coord_2.lng = test_coordinates
    return coord_1, coord_2


@pytest.fixture
def test_geometry(mock_geocoordinates):
    return Geometry(mock_geocoordinates)


@pytest.fixture
def mock_geometry(mock_geocoordinates):
    coord_1, coord_2 = mock_geocoordinates
    return Geometry([coord_1, coord_2])  # TODO: mock Geometry as well
