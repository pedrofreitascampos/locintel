from das.routing.traces.samplers import SimpleSampler

from tests.fixtures import *


class TestSimpleSampler(object):
    def test_simple_sampler(self, mock_trace):
        result = SimpleSampler(period=3).sample(mock_trace)

        assert result.probes == [
            mock_trace.probes[0],
            mock_trace.probes[3],
            mock_trace.probes[-1],
        ]
        assert result.identifier == mock_trace.identifier

    def test_sample_1_period_returns_same_trace(self, mock_trace):
        result = SimpleSampler(period=1).sample(mock_trace)

        assert result.probes == mock_trace.probes
        assert result.identifier == mock_trace.identifier

    def test_sample_period_longer_than_number_of_probes_returns_start_end(
        self, mock_trace
    ):
        result = SimpleSampler(period=10).sample(mock_trace)

        assert result.probes == [mock_trace.probes[0], mock_trace.probes[-1]]
        assert result.identifier == mock_trace.identifier

    def test_returns_new_trace_does_not_modify_original(self, mock_trace):
        mock_trace_length = len(mock_trace.probes)

        SimpleSampler(period=3).sample(mock_trace)

        assert mock_trace_length == len(mock_trace.probes)
