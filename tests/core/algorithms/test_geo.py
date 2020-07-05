from math import isclose

from locintel.core.datamodel.geo import GeoCoordinate
from locintel.core.algorithms.geo import calculate_angle

import pytest


def test_get_angle():
    a = GeoCoordinate(1.0, 1.0)
    b = GeoCoordinate(2.0, 2.0)
    c = GeoCoordinate(1.0, 2.0)
    assert isclose(calculate_angle(a, b, c), 90.0, rel_tol=1e-6)
    assert isclose(calculate_angle(c, b, a), 45.0, rel_tol=1e-6)
