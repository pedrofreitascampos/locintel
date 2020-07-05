from locintel.traces.filters import LowConfidenceFilter, TimeGapFilter

import pytest

from tests.fixtures import *


class TestTraceFilterLowConfidence(object):
    def test_low_confidence_filter(self, mock_trace):
        assert LowConfidenceFilter().filter(mock_trace) is True

    def test_custom_threshold(self, mock_trace):
        assert LowConfidenceFilter(min_confidence=2).filter(mock_trace) is False

    def test_raises_value_error_if_any_probe_missing_confidence(self, mock_trace):
        delattr(mock_trace.probes[1], "confidence")
        with pytest.raises(ValueError):
            LowConfidenceFilter().filter(mock_trace)


class TestTraceTimeGapFilter(object):
    def test_time_gap_filter(self, mock_trace):
        assert TimeGapFilter().filter(mock_trace) is True

    def test_custom_threshold(self, mock_trace):
        assert TimeGapFilter(max_time_gap_seconds=1).filter(mock_trace) is False

    def test_raises_value_error_if_any_probe_missing_time(self, mock_trace):
        delattr(mock_trace.probes[1], "time")
        with pytest.raises(ValueError):
            TimeGapFilter().filter(mock_trace)
