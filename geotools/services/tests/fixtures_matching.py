import pytest
from unittest.mock import Mock

das_match_response = {
    "code": "Ok",
    "matchNumber": 1,
    "matchings": [
        {
            "confidence": 0.9,
            "legs": [
                {
                    "traceFromIndex": 0,
                    "traceToIndex": 1,
                    "duration": 7.3,
                    "distance": 91.1,
                    "nodes": [3630503033, 65665981, 65485527, 3633745188],
                    "geometry": [{"lat": 0, "lon": 1}, {"lat": 2, "lon": 3}],
                },
                {
                    "traceFromIndex": 1,
                    "traceToIndex": 2,
                    "duration": 5,
                    "distance": 62.6,
                    "nodes": [65485527, 3633745188, 65457254],
                    "geometry": [{"lat": 3, "lon": 4}, {"lat": 5, "lon": 6}],
                },
            ],
        }
    ],
    "tracepoints": [
        {"snapDistance": 0, "location": {"lon": 0, "lat": 0}},
        {"snapDistance": 2, "location": {"lon": 1, "lat": 0}},
        {"snapDistance": 0, "location": {"lon": 2, "lat": 0}},
        {},
    ],
}


@pytest.fixture()
def setup_das_matcher_environment(mocker):
    response_mock = Mock(
        json=Mock(return_value=das_match_response), elapsed=Mock(microseconds=100)
    )
    mocker.patch("requests.post", return_value=response_mock)
    expected_match = Mock(
        geometry=Mock(
            coords=[
                Mock(lat=0, lng=1),
                Mock(lat=2, lng=3),
                Mock(lat=3, lng=4),
                Mock(lat=5, lng=6),
            ]
        ),
        distance=62.6 + 91.1,
        duration=5 + 7.3,
        metadata={
            "confidence": 0.9,
            "max_snap_distance": 2,
            "failed_points": 1,
            "raw": das_match_response,
        },
    )
    return {"response_mock": response_mock, "expected_match": expected_match}
