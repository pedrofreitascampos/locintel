from locintel.core.datamodel.traces import Probe, Trace

import pytest
from unittest.mock import Mock

from tests.fixtures.traces import *


class TestProbe(object):
    def test_probe(self, mock_probe):
        lat, lng, time, heading, confidence = mock_probe
        result = Probe(lat, lng, time, heading, confidence)

        assert result.lat == mock_probe[0]
        assert result.lng == mock_probe[1]
        assert result.time == mock_probe[2]
        assert result.bearing == mock_probe[3]
        assert result.confidence == mock_probe[4]

    def test_invalid_lat_raises_value_error(self, mock_probe):
        mock_probe[0] = 3000
        with pytest.raises(ValueError):
            Probe(*mock_probe)

    def test_invalid_lat_type_raises_type_error(self, mock_probe):
        mock_probe[0] = "invalid_type"
        with pytest.raises(TypeError):
            Probe(*mock_probe)

    def test_invalid_lng_raises_value_error(self, mock_probe):
        mock_probe[1] = 3000
        with pytest.raises(ValueError):
            Probe(*mock_probe)

    def test_invalid_lng_type_raises_type_error(self, mock_probe):
        mock_probe[1] = "invalid_type"
        with pytest.raises(TypeError):
            Probe(*mock_probe)

    def test_invalid_time_type_raises_type_error(self, mock_probe):
        mock_probe[2] = "invalid_type"
        with pytest.raises(TypeError):
            Probe(*mock_probe)

    def test_invalid_heading_raises_value_error(self, mock_probe):
        mock_probe[3] = 30000
        with pytest.raises(ValueError):
            Probe(*mock_probe)

    def test_from_druid(self, mock_probe):
        lat, lng, time, heading, confidence = mock_probe
        probe = {
            "event": {
                "coordinatelatitude": lat,
                "coordinatelongitude": lng,
                "timestamp": time.isoformat(),
            }
        }

        result = Probe.from_druid(probe)

        assert result.lat == lat
        assert result.lng == lng
        assert result.time == time
        assert not result.bearing
        assert not result.confidence


class TestTrace(object):
    def test_trace(self):
        identifier = "id1"
        probes = [Mock(Probe), Mock(Probe), Mock(Probe)]
        result = Trace(probes=probes, identifier=identifier)

        assert result.probes == probes
        assert result.identifier == identifier

    def test_getitem_returns_points(self):
        probes = [Mock(Probe), Mock(Probe), Mock(Probe)]
        result = Trace(probes=probes)

        assert result[0] == result.probes[0]
        assert result[-1] == result.probes[-1]

    def test_iterator_returns_points_iterator(self):
        probes = [Mock(Probe), Mock(Probe), Mock(Probe)]
        result = Trace(probes=probes)

        assert list(result) == result.probes
