from locintel.core.datamodel.traces import Trace


class TraceSampling(object):
    def __init__(self, name):
        self.name = name

    def sample(self, trace, *args, **kwargs):
        raise NotImplementedError("Implement subclass")


class SimpleSampler(TraceSampling):
    def __init__(self, period=5):
        super().__init__(name="simple")
        self.period = period

    def sample(self, trace, *args, **kwargs):
        sampled_probes = trace.probes[:: self.period]
        if trace.probes[-1] not in sampled_probes:
            sampled_probes.append(trace.probes[-1])
        return Trace(sampled_probes, identifier=trace.identifier)
