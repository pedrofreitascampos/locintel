from enum import Enum


class FileType(Enum):
    JURBEY = 1
    GEOJSON = 2
    GRAPHML = 3


class EdgeType(Enum):
    CONNECTION_TURN_LEFT = "CONNECTION_TURN_LEFT"
    CONNECTION_TURN_RIGHT = "CONNECTION_TURN_RIGHT"
    CONNECTION_UTURN = "CONNECTION_UTURN"
    CONNECTION_MERGE = "CONNECTION_MERGE"
    CONNECTION_FORK = "CONNECTION_FORK"
    CONNECTION_STRAIGHT = "CONNECTION_STRAIGHT"
    LANE_STRAIGHT = "LANE_STRAIGHT"
    LANE_CHANGE = "LANE_CHANGE"


class RestrictionType(Enum):
    RESTRICTED_TURN = "RESTRICTED_TURN"


class SignType(Enum):
    SpeedLimit = 1
    Regulatory = 2
    WarningSign = 3
    Guide = 4
    Expressway = 5
    TrafficLight = 6


class VehicleType(Enum):
    Car = 1
    Bus = 2
    Taxi = 3
    Emergency = 4
    Truck = 5
    All = 6


class RoadClass(Enum):
    Highway = 1
    MajorRoad = 2
    LocalRoad = 3
    DirtRoad = 4


class RoadAccessibility(Enum):
    NoRestriction = 1
    Private = 2
    Service = 3
    HOV = 4
