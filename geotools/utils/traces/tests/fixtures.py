from datetime import datetime
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_probe():
    return [10, 20, datetime(1970, 1, 1), 50, 0.1]


@pytest.fixture
def mock_trace():
    probes = [
        Mock(confidence=1.0, time=datetime(1970, 1, 1, 0, 1)),
        Mock(confidence=1.5, time=datetime(1970, 1, 1, 0, 2)),
        Mock(confidence=1.7, time=datetime(1970, 1, 1, 0, 3)),
        Mock(confidence=1.9, time=datetime(1970, 1, 1, 0, 4)),
        Mock(confidence=2.1, time=datetime(1970, 1, 1, 0, 5)),
    ]
    return Mock(probes=probes)
