from copy import deepcopy
import itertools
import os
from pydruid.client import PyDruid

from das.routing.core.datamodel.traces import Trace, Probe


class BaseLoader(object):
    def __init__(self, name):
        self.name = name


class DruidLoader(BaseLoader):
    def __init__(
        self,
        url="https://druid.broker.develop.otonomousmobility.com/",
        endpoint="druid/v2",
        datasource="mytaxi_gps_probes_index_parallel_v4",
        username=None,
        password=None,
    ):
        super().__init__("druid")
        self.url = url
        self.endpoint = endpoint
        self.datasource = datasource
        self.connector = PyDruid(url, endpoint)
        self.connector.set_basic_auth_credentials(
            username or os.environ["USERNAME"], password or os.environ["PASSWORD"]
        )

        interval = self.connector.time_boundary(datasource=self.datasource).result[0][
            "result"
        ]
        self.interval = f'{interval["minTime"]}/{interval["maxTime"]}'
        self.default_query = {
            "datasource": self.datasource,
            "granularity": "all",
            "intervals": self.interval,
            "paging_spec": {"paging_identifiers": {}, "threshold": 100},
        }

    def load(self, **kwargs):
        query = deepcopy(self.default_query)
        query.update(kwargs)
        for trace in self.connector.select(**query):
            probes = [Probe.from_druid(probe) for probe in trace["result"]["events"]]
            yield Trace(probes, identifier=self._extract_booking_id(trace))

    @staticmethod
    def _extract_booking_id(trace):
        probe_groups = {
            k: len(list(v))
            for k, v in itertools.groupby(
                trace["result"]["events"], key=lambda event: event["event"]["bookingid"]
            )
        }
        if len(probe_groups) > 1:
            raise ValueError(
                f"Trace has probes from different bookings: {probe_groups.keys()}"
            )

        return list(probe_groups.keys())[0]
