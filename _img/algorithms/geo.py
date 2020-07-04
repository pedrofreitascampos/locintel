import math
import numpy as np

earth_radius = 6373


def dot_product(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def vector_length(v):
    return math.sqrt(dot_product(v, v))


def angle(v1, v2):
    return math.acos(dot_product(v1, v2) / (vector_length(v1) * vector_length(v2)))


def degrees_to_radians(deg):
    return deg * math.pi / 180


def radians_to_degrees(rad):
    return rad * 180 / math.pi


def distance_to_radians(distance):
    return distance / earth_radius


def radians_to_distance(radians):
    return radians * earth_radius


def bearing(start, end):
    lon1 = degrees_to_radians(start[0])
    lon2 = degrees_to_radians(end[0])
    lat1 = degrees_to_radians(start[1])
    lat2 = degrees_to_radians(end[1])

    a = math.sin(lon2 - lon1) * math.cos(lat2)

    b = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        lon2 - lon1
    )

    return radians_to_degrees(math.atan2(a, b))


def destination(origin, distance, bearing):
    longitude1 = degrees_to_radians(origin[0])
    latitude1 = degrees_to_radians(origin[1])
    bearing_rads = degrees_to_radians(bearing)

    radians = distance_to_radians(distance)

    latitude2 = math.asin(
        math.sin(latitude1) * math.cos(radians)
        + math.cos(latitude1) * math.sin(radians) * math.cos(bearing_rads)
    )

    longitude2 = longitude1 + math.atan2(
        math.sin(bearing_rads) * math.sin(radians) * math.cos(latitude1),
        math.cos(radians) - math.sin(latitude1) * math.sin(latitude2),
    )

    lng = radians_to_degrees(longitude2)
    lat = radians_to_degrees(latitude2)

    return [lng, lat]


def measure_distance(coordinates1, coordinates2):

    dLat = degrees_to_radians(coordinates2[1] - coordinates1[1])
    dLon = degrees_to_radians(coordinates2[0] - coordinates1[0])

    lat1 = degrees_to_radians(coordinates1[1])
    lat2 = degrees_to_radians(coordinates2[1])

    a = math.pow(math.sin(dLat / 2), 2) + math.pow(math.sin(dLon / 2), 2) * math.cos(
        lat1
    ) * math.cos(lat2)

    return radians_to_distance(2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def calculate_angle(a, b, c):
    """
    Returns angle (a-b-c), in degrees

    All points are assumed to be das.routing.core.datamodel.geo.GeoCoordinate objects
    """
    b_c = math.sqrt((b.lng - c.lng) ** 2 + (b.lat - c.lat) ** 2)
    a_c = math.sqrt((a.lng - c.lng) ** 2 + (a.lat - c.lat) ** 2)
    a_b = math.sqrt((a.lng - b.lng) ** 2 + (a.lat - b.lat) ** 2)
    formula = (b_c ** 2.0 + a_c ** 2.0 - a_b ** 2.0) / (2.0 * b_c * a_c)
    formula = -1.0 if formula < -1.0 else formula
    formula = 1.0 if formula > 1.0 else formula
    return (math.acos(formula) * 180.0) / math.pi


def project_along_line(coords, distance):
    travelled = 0
    for i in range(len(coords)):
        if distance >= travelled and i == len(coords) - 1:
            break
        elif travelled >= distance:
            overshot = distance - travelled
            if not overshot:
                return coords[i]
            else:
                direction = bearing(coords[i], coords[i - 1]) - 180
                interpolated = destination(coords[i], overshot, direction)
                return interpolated
        else:
            travelled += measure_distance(coords[i], coords[i + 1])

    return coords[-1]


def length(coords):
    total_distance = 0
    for i in range(len(coords)):
        if i == len(coords) - 2:
            break
        else:
            total_distance += measure_distance(coords[i], coords[i + 1])

    return total_distance


def frechet_distance(geo1, geo2, i=0, j=0, distance_matrix=None):
    """
    Recursively computes the discrete frechet distance between two geometries

    Algorithm: http://www.kr.tuwien.ac.at/staff/eiter/et-archive/cdtr9464.pdf

    :param geo1: das.routing.core.datamodel.geo.Geometry object 1
    :param geo2: das.routing.core.datamodel.geo.Geometry object 2
    :param i: index for geo1 traversal
    :param j: index for geo2 traversal
    :param distance_matrix: distance matrix between geo1 points and geo2 points (None for initialization)
    """
    if distance_matrix is None:
        distance_matrix = np.ones((len(geo1), len(geo2)))
        distance_matrix = np.multiply(distance_matrix, -1)

    # i, j are the indices of geo1, and geo2 traversals, respectively
    if distance_matrix[i, j] > -1:
        return distance_matrix[i, j]

    if i == 0 and j == 0:
        distance_matrix[i, j] = geo1[0].distance_to(geo2[0])
    elif i > 0 and j == 0:
        distance_matrix[i, j] = max(
            frechet_distance(geo1, geo2, i - 1, 0, distance_matrix),
            geo1[i].distance_to(geo2[0]),
        )
    elif i == 0 and j > 0:
        distance_matrix[i, j] = max(
            frechet_distance(geo1, geo2, 0, j - 1, distance_matrix),
            geo1[0].distance_to(geo2[j]),
        )
    elif i > 0 and j > 0:
        distance_matrix[i, j] = max(
            min(
                frechet_distance(geo1, geo2, i - 1, j, distance_matrix),
                frechet_distance(geo1, geo2, i - 1, j - 1, distance_matrix),
                frechet_distance(geo1, geo2, i, j - 1, distance_matrix),
            ),
            geo1[i].distance_to(geo2[j]),
        )
    else:
        distance_matrix[i, j] = float("inf")
    return distance_matrix[i, j]


def create_vector(nodes):
    x = nodes[-1].coord.lng - nodes[0].coord.lng
    y = nodes[-1].coord.lat - nodes[0].coord.lat
    return x, y


def calculate_direction(v1, v2):
    if len(v1) != 2 or len(v2) != 2:
        raise ValueError("Vectors must have 2 dimensions")

    matrix = np.transpose([v1, v2])
    det = np.linalg.det(matrix)

    if det > 0:
        return "no_left_turn"

    if det < 0:
        return "no_right_turn"

    return "no_u_turn"
