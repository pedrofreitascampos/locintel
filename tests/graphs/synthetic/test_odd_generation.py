"""
Generative/synthetic tests for graph masking methods. Rationale is to create multiple scenarios programatically and
test ODD restriction methods against those.

See more details here: https://gitlab.mobilityservices.io/am/roam/routing/issues/169

There are two main entities:
* Scenarios
* Methods

Scenarios are essentially test cases emulating possible scenarios for odd generation, and always involve the generation
of a base graph and an ODD graph. All scenarios are defined in `scenarios.py` - see module for instructions.

Methods are the odd generation methods to test against the scenarios. A function which applies the method is expected
as well as a setup function, which prepares required artifacts and resources from the graphs generated in "scenarios".
Methods to test and respective setups are enumerated defined in `method_drivers.py` - see module for instructions.
"""
from itertools import product

import pytest

from tests.synthetic.method_drivers import (
    SimpleGraphMatchingDriver,
    RouteMatchingMethodDriver,
)
from tests.synthetic.scenarios import scenarios

methods = [RouteMatchingMethodDriver(), SimpleGraphMatchingDriver()]


@pytest.fixture
def run_test(method, scenario):
    base_artifact, odd_artifact = method.setup(
        scenario.base_graph, scenario.input_graph
    )
    yield method.apply(base_artifact, odd_artifact)
    method.teardown()


@pytest.mark.parametrize(
    "method, scenario", list(product(methods, scenarios)), ids=lambda x: x.name
)
def test_odd_generation(method, scenario, run_test):
    resulting_graph = run_test

    assert resulting_graph == scenario.expected_graph
