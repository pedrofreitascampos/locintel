import datetime as dt


class TraceFilter(object):
    def __init__(self, name):
        self.name = name

    def filter(self, trace, *args, **kwargs):
        raise NotImplementedError("Implement subclass")


class LowConfidenceFilter(TraceFilter):
    """
    Determines whether a trace satisfies a certain threshold for lowest probe confidence
    """

    def __init__(self, min_confidence=0.7):
        super().__init__("low_confidence")
        self.threshold = min_confidence

    def filter(self, trace, *args, **kwargs):
        try:
            min_confidence = min([probe.confidence for probe in trace.probes])
        except AttributeError:
            raise ValueError(
                "Some probe points do not contain confidence information, cannot use this filter"
            )

        if min_confidence < self.threshold:
            return False
        return True


class TimeGapFilter(TraceFilter):
    """
    Determines whether a trace satisfies a certain threshold for time gap between probes
    """

    def __init__(self, max_time_gap_seconds=120):
        super().__init__("time_gaps")
        self.threshold = max_time_gap_seconds

    def filter(self, trace, *args, **kwargs):
        try:
            max_gap = max(
                [
                    probe2.time - probe1.time
                    for probe1, probe2 in zip(trace.probes[::2], trace.probes[1::2])
                ]
            )
        except AttributeError:
            raise ValueError(
                "Some probe points do not contain time information, cannot use this filter"
            )

        if max_gap > dt.timedelta(seconds=self.threshold):
            return False
        return True
