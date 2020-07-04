import random
import shapely.geometry as sg

from das.routing.quality.generators.random import RandomRoutePlanGenerator, polygons

random.seed(10)


class TestRandomRoutePlanGenerator(object):
    def test_random_route_plan_generator(self):
        polygon = polygons["berlin"]
        generator = RandomRoutePlanGenerator()

        route_plan = generator.generate_route(polygon)

        assert polygon.contains(sg.Point(route_plan.start.lng, route_plan.start.lat))
        assert polygon.contains(sg.Point(route_plan.end.lng, route_plan.end.lat))
        assert generator.name == "random"

    def test_random_route_plan_generator_accepts_identifier(self):
        polygon = polygons["berlin"]
        generator = RandomRoutePlanGenerator()
        identifier = "id1"

        route_plan = generator.generate_route(polygon, identifier=identifier)

        assert polygon.contains(sg.Point(route_plan.start.lng, route_plan.start.lat))
        assert polygon.contains(sg.Point(route_plan.end.lng, route_plan.end.lat))
        assert route_plan.identifier == identifier
        assert generator.name == "random"
