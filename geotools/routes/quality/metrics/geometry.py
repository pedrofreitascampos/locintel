from dtw import dtw
import inspect
import math
import shapely.geometry as sg

from das.routing.core.algorithms.geo import frechet_distance
from das.routing.core.algorithms.strings import levenshtein_distance


class GeometryComparator(object):
    def __init__(self):
        self.methods = [
            method[0].lstrip("compare_")
            for method in inspect.getmembers(self)
            if "compare_" in method[0]
        ]

    def compare(self, geo1, geo2, method, **kwargs):
        try:
            func = getattr(self, f"compare_{method}")
        except AttributeError:
            raise AttributeError(
                f'"{method}" not a valid method, choose from: {self.methods}'
            )
        return func(geo1, geo2, **kwargs)

    @staticmethod
    def compare_hausdorff(geo1, geo2, square=False, modifier_func=None):
        """
        Calculates Hausdorff distance (see shapely.geometry.hausdorff_distance)

        :param square: whether to calculate square of distances (increases significance of big differences)
        :param modifier_func: custom function to apply to hausdorff
        """
        geo1 = geo1.to_linestring(convert_to_utm=True)
        geo2 = geo2.to_linestring(convert_to_utm=True)
        distance = geo1.hausdorff_distance(geo2)
        if square:
            return distance ** 2
        elif modifier_func:
            return modifier_func(distance)
        else:
            return distance

    @staticmethod
    def compare_frechet(geo1, geo2):
        """
        Calculates Frechet distance (see das.routing.core.algorithms.geo.frechet_distance)
        """
        return frechet_distance(geo1, geo2, len(geo1) - 1, len(geo2) - 1)

    @staticmethod
    def compare_dtw(geo1, geo2):
        """
        Calculates Dynamic Time Warped distance
        """
        return dtw(geo1, geo2, dist=lambda point1, point2: point1.distance_to(point2))[
            0
        ]

    @staticmethod
    def compare_centroids(geo1, geo2):
        """
        Calculate euclidean distance between centers of mass of both geometries
        """
        return geo1.to_linestring(convert_to_utm=True).centroid.distance(
            geo2.to_linestring(convert_to_utm=True).centroid
        )

    @staticmethod
    def compare_auc(geo1, geo2, normalized=False):
        """
        Calculate the Area under the curves describes by both geometries

        :param normalized: Calculates AUC as ratio of envelope over the two geometries
        """
        utm_linestring_1 = geo1.to_linestring(convert_to_utm=True)
        utm_linestring_2 = geo2.to_linestring(convert_to_utm=True)

        polygon = sg.Polygon(
            list(utm_linestring_1.coords) + list(utm_linestring_2.coords)[::-1]
        )
        auc = polygon.area

        if normalized:
            auc = 1 - auc / polygon.envelope.area

        return auc

    @staticmethod
    def compare_bocs(geo1, geo2):
        """
        Bias-Outlier Composite Score: considers consistent differences (area-based) and large
        outliers (max distance)-based, by combining them with a geometric mean
        """
        max_distance = GeometryComparator.compare_hausdorff(geo1, geo2)
        auc = GeometryComparator.compare_auc(geo1, geo2)
        return math.sqrt(math.pow(max_distance, 2) + math.pow(auc, 2))

    @staticmethod
    def compare_pmr(geo1, geo2, buffer=10):
        """
        Point Match Ratio: % of points within buffer of other geometry

        :param buffer: corridor width to consider, in meters
        """
        total_points = len(geo1) + len(geo2)
        line1 = geo1.to_linestring(convert_to_utm=True)
        line2 = geo2.to_linestring(convert_to_utm=True)

        good_points = 0
        for point in geo1:
            if point.to_shapely_point(convert_to_utm=True).distance(line2) <= buffer:
                good_points += 1

        for point in geo2:
            if point.to_shapely_point(convert_to_utm=True).distance(line1) <= buffer:
                good_points += 1

        return good_points / total_points

    @staticmethod
    def compare_levenshtein(geo1, geo2):
        """
        Frame geometry comparison as string matching problem by transforming geometries into google encoded polyline

        See
        """
        return levenshtein_distance(geo1.to_polyline(), geo2.to_polyline())
