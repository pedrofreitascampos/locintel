from das.routing.traces.loaders import DruidLoader

import pytest
from unittest.mock import Mock, patch, call


@pytest.fixture
def fake_config():
    return "https://fakeurl.com", "/endpoint/v1", "datasource", "user", "password"


@pytest.fixture
def mock_connector():
    interval = "1970/1981"
    druid_connector_mock = Mock()
    druid_connector_mock.interval = interval
    druid_connector_mock.set_basic_auth_credentials = Mock()
    druid_connector_mock.time_boundary = Mock(
        return_value=Mock(
            result=[
                {
                    "result": {
                        "minTime": interval.split("/")[0],
                        "maxTime": interval.split("/")[1],
                    }
                }
            ]
        )
    )

    event = {"event": {"bookingid": 1}}
    probe1 = Mock(__getitem__=lambda x, y: event.__getitem__(y))
    probe2 = Mock(__getitem__=lambda x, y: event.__getitem__(y))
    probe3 = Mock(__getitem__=lambda x, y: event.__getitem__(y))
    result1 = {"result": {"events": [probe1, probe2, probe3]}}
    result2 = {"result": {"events": [probe1, probe1, probe2]}}
    results = [result1, result2]
    druid_connector_mock.select = Mock(return_value=results)
    druid_connector_mock.result1 = result1
    druid_connector_mock.result2 = result2
    druid_connector_mock.probe1 = probe1
    druid_connector_mock.probe2 = probe2
    druid_connector_mock.probe3 = probe3
    return druid_connector_mock


class TestDruidLoader(object):
    @patch("das.routing.traces.loaders.PyDruid")
    def test_druid_loader(self, druid_mock, mock_connector, fake_config):
        url, endpoint, datasource, user, password = fake_config
        druid_mock.return_value = mock_connector

        loader = DruidLoader(
            url=url,
            endpoint=endpoint,
            datasource=datasource,
            username=user,
            password=password,
        )

        assert loader.url == url
        assert loader.endpoint == endpoint
        assert loader.datasource == datasource
        assert not getattr(loader, "username", None)
        assert not getattr(loader, "password", None)
        assert loader.connector == mock_connector
        assert loader.interval == mock_connector.interval
        assert loader.default_query["datasource"] == datasource
        assert loader.default_query["intervals"] == mock_connector.interval
        druid_mock.assert_called_with(url, endpoint)
        mock_connector.set_basic_auth_credentials.assert_called_with(user, password)
        mock_connector.time_boundary.assert_called_with(datasource=datasource)

    @patch("das.routing.traces.loaders.PyDruid")
    @patch("das.routing.traces.loaders.Probe")
    @patch("das.routing.traces.loaders.Trace")
    def test_load(
        self, trace_mock, probe_mock, druid_mock, mock_connector, fake_config
    ):
        url, endpoint, datasource, user, password = fake_config
        druid_mock.return_value = mock_connector
        probes = [Mock(), Mock(), Mock(), Mock(), Mock(), Mock()]  # Called 6 times
        probe_mock.from_druid = Mock(side_effect=probes)
        traces = [Mock(), Mock()]
        trace_mock.side_effect = traces

        loader = DruidLoader(
            url=url,
            endpoint=endpoint,
            datasource=datasource,
            username=user,
            password=password,
        )
        result = list(loader.load())

        assert result == traces
        probe_mock.from_druid.assert_has_calls(
            [
                call(mock_connector.probe1),
                call(mock_connector.probe2),
                call(mock_connector.probe3),
                call(mock_connector.probe1),
                call(mock_connector.probe1),
                call(mock_connector.probe2),
            ]
        )
        trace_mock.assert_has_calls(
            [call(probes[:3], identifier=1), call(probes[3:], identifier=1)]
        )
