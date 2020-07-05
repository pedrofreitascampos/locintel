import shapely.geometry as sg

import pytest
from unittest.mock import Mock, MagicMock

from locintel.quality.metrics.geometry import GeometryComparator
from locintel.core.datamodel.geo import Geometry


class TestGeometryComparator(object):
    def test_geometry_comparator(self):
        geo1, geo2 = Mock(Geometry), Mock(Geometry)
        method = "method"
        kwargs = {"arg1": 1, "arg2": 2}
        comparison_result = 5

        comparator = GeometryComparator()
        comparator.compare_method = Mock(return_value=comparison_result)

        result = comparator.compare(geo1, geo2, method, **kwargs)

        assert result == comparison_result
        comparator.compare_method.assert_called_with(geo1, geo2, **kwargs)

    def test_geometry_comparator_raises_attribute_error_when_method_does_not_exist(
        self
    ):
        geo1, geo2 = Mock(Geometry), Mock(Geometry)
        method = "inexistent_method"
        kwargs = {"arg1": 1, "arg2": 2}

        with pytest.raises(AttributeError):
            GeometryComparator().compare(geo1, geo2, method, **kwargs)

    def test_compare_hausdorff(self):
        distance = 5
        line1, line2 = Mock(hausdorff_distance=Mock(return_value=distance)), Mock()
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )

        result = GeometryComparator.compare_hausdorff(geo1, geo2)

        assert result == distance
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        line1.hausdorff_distance.assert_called_with(line2)

    def test_compare_hausdorff_squared(self):
        distance = 5
        line1, line2 = Mock(hausdorff_distance=Mock(return_value=distance)), Mock()
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )

        result = GeometryComparator.compare_hausdorff(geo1, geo2, square=True)

        assert result == distance ** 2
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        line1.hausdorff_distance.assert_called_with(line2)

    def test_compare_hausdorff_with_modifier_func(self):
        distance = 5
        line1, line2 = Mock(hausdorff_distance=Mock(return_value=distance)), Mock()
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )

        result = GeometryComparator.compare_hausdorff(
            geo1, geo2, modifier_func=lambda x: x + 1
        )

        assert result == distance + 1
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        line1.hausdorff_distance.assert_called_with(line2)

    def test_compare_frechet(self, mocker):
        distance = 5
        len1, len2 = 5, 10
        geo1, geo2 = (
            Mock(Geometry, __len__=lambda _: len1),
            Mock(Geometry, __len__=lambda _: len2),
        )
        mocker.patch(
            "locintel.quality.metrics.geometry.frechet_distance",
            return_value=distance,
        )

        result = GeometryComparator.compare_frechet(geo1, geo2)

        assert result == distance

    def test_compare_dtw(self, mocker):
        distance = 5
        geo1, geo2 = Mock(Geometry), Mock(Geometry)
        mocker.patch(
            "locintel.quality.metrics.geometry.dtw", return_value=[distance]
        )

        result = GeometryComparator.compare_dtw(geo1, geo2)

        assert result == distance

    def test_compare_centroids(self):
        distance = 5
        distance_mock = Mock(return_value=distance)
        line1, line2 = (
            Mock(centroid=Mock(distance=distance_mock)),
            Mock(centroid=Mock()),
        )
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )

        result = GeometryComparator.compare_centroids(geo1, geo2)

        assert result == distance
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        distance_mock.assert_called_with(line2.centroid)

    def test_compare_auc(self, mocker):
        area = 5
        polygon_mock = Mock(area=area)
        line1_coords, line2_coords = [Mock()], [Mock(), Mock()]
        line1, line2 = (
            Mock(coords=line1_coords),
            Mock(coords=line2_coords, __iter__=iter(line2_coords)),
        )
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )
        mocker.patch("shapely.geometry.Polygon", return_value=polygon_mock)

        result = GeometryComparator.compare_auc(geo1, geo2)

        assert result == area
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        sg.Polygon.assert_called_with(line1_coords + line2_coords[::-1])

    def test_compare_auc_normalized(self, mocker):
        area = 5
        envelope_area = 10
        polygon_mock = Mock(area=area, envelope=Mock(area=envelope_area))
        line1_coords, line2_coords = [Mock()], [Mock(), Mock()]
        line1, line2 = (
            Mock(coords=line1_coords),
            Mock(coords=line2_coords, __iter__=iter(line2_coords)),
        )
        geo1, geo2 = (
            Mock(Geometry, to_linestring=Mock(return_value=line1)),
            Mock(Geometry, to_linestring=Mock(return_value=line2)),
        )
        mocker.patch("shapely.geometry.Polygon", return_value=polygon_mock)

        result = GeometryComparator.compare_auc(geo1, geo2, normalized=True)

        assert result == 0.5  # 1 - area/envelope_area
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        sg.Polygon.assert_called_with(line1_coords + line2_coords[::-1])

    def test_compare_bocs(self, mocker):
        hausdorff = 3
        auc = 4
        bocs = 5  # math.sqrt(3**2 + 4**2)
        mocker.patch(
            "locintel.quality.metrics.geometry.GeometryComparator.compare_hausdorff",
            return_value=hausdorff,
        )
        mocker.patch(
            "locintel.quality.metrics.geometry.GeometryComparator.compare_auc",
            return_value=auc,
        )
        geo1, geo2 = Mock(Geometry), Mock(Geometry)

        result = GeometryComparator.compare_bocs(geo1, geo2)

        assert result == bocs

    def test_compare_pmr(self):
        """
        Scenario:
            Geo1:   1-----------2

            Geo2:   1-----------2\
                                  \
                                   \
                                    \
                                     \
                                      3

        All points are within buffer distance of the other geometry, except for point 3 of geo2 -> PMR=0.8
        """
        buffer = 10
        inside_buffer = 5
        outside_buffer = 11
        line1_shapely1_distance_mock = Mock(return_value=inside_buffer)
        line1_shapely2_distance_mock = Mock(return_value=inside_buffer)
        line2_shapely1_distance_mock = Mock(return_value=inside_buffer)
        line2_shapely2_distance_mock = Mock(return_value=inside_buffer)
        line2_shapely3_distance_mock = Mock(return_value=outside_buffer)
        line1_shapely1 = Mock(distance=line1_shapely1_distance_mock)
        line1_shapely2 = Mock(distance=line1_shapely2_distance_mock)
        line2_shapely1 = Mock(distance=line2_shapely1_distance_mock)
        line2_shapely2 = Mock(distance=line2_shapely2_distance_mock)
        line2_shapely3 = Mock(distance=line2_shapely3_distance_mock)
        line1_coord1, line1_coord2 = (
            Mock(to_shapely_point=Mock(return_value=line1_shapely1)),
            Mock(to_shapely_point=Mock(return_value=line1_shapely2)),
        )
        line2_coord1, line2_coord2, line2_coord3 = (
            Mock(to_shapely_point=Mock(return_value=line2_shapely1)),
            Mock(to_shapely_point=Mock(return_value=line2_shapely2)),
            Mock(to_shapely_point=Mock(return_value=line2_shapely3)),
        )
        line1, line2 = Mock(), Mock()
        geo1 = MagicMock(
            Geometry,
            __len__=Mock(return_value=2),
            to_linestring=Mock(return_value=line1),
        )
        geo1.__iter__.return_value = [line1_coord1, line1_coord2]
        geo2 = MagicMock(
            Geometry,
            __len__=Mock(return_value=3),
            to_linestring=Mock(return_value=line2),
        )
        geo2.__iter__.return_value = [line2_coord1, line2_coord2, line2_coord3]

        result = GeometryComparator.compare_pmr(geo1, geo2, buffer=buffer)

        assert result == 0.8  # 4 point inside the buffer, 1 out
        geo1.to_linestring.assert_called_with(convert_to_utm=True)
        geo2.to_linestring.assert_called_with(convert_to_utm=True)
        line1_coord1.to_shapely_point.assert_called_with(convert_to_utm=True)
        line1_coord2.to_shapely_point.assert_called_with(convert_to_utm=True)
        line2_coord1.to_shapely_point.assert_called_with(convert_to_utm=True)
        line2_coord2.to_shapely_point.assert_called_with(convert_to_utm=True)
        line2_coord3.to_shapely_point.assert_called_with(convert_to_utm=True)
        line1_shapely1_distance_mock.assert_called_with(line2)
        line1_shapely2_distance_mock.assert_called_with(line2)
        line2_shapely1_distance_mock.assert_called_with(line1)
        line2_shapely2_distance_mock.assert_called_with(line1)
        line2_shapely3_distance_mock.assert_called_with(line1)

    def test_compare_levenshtein(self, mocker):
        levenshtein = 10
        levenshtein_mock = Mock(return_value=levenshtein)
        mocker.patch(
            "locintel.quality.metrics.geometry.levenshtein_distance",
            side_effect=levenshtein_mock,
        )
        poly1, poly2 = Mock(), Mock()
        geo1, geo2 = (
            Mock(Geometry, to_polyline=Mock(return_value=poly1)),
            Mock(Geometry, to_polyline=Mock(return_value=poly2)),
        )

        result = GeometryComparator.compare_levenshtein(geo1, geo2)

        assert result == levenshtein
        levenshtein_mock.assert_called_with(poly1, poly2)
