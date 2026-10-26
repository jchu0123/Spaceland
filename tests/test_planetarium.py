import json
import unittest

from app import app
from planetarium import FACT_KEYS, PlanetariumAgent, ScoutIntentRouter, load_planets, load_solar_bodies


class OfflineDatabase:
    def get_planet(self, _name):
        return None


class OfflineModel:
    def rephrase(self, _question, _answer, _records):
        return None


class PlanetCatalogTests(unittest.TestCase):
    def test_eight_planets_share_twelve_facts(self):
        planets = load_planets()
        self.assertEqual(len(planets), 8)
        self.assertEqual([planet["name"] for planet in planets], [
            "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"
        ])
        for planet in planets:
            self.assertEqual(set(planet["facts"]), set(FACT_KEYS), planet["name"])
            self.assertEqual(len(planet["facts"]), 12, planet["name"])
            self.assertTrue(planet["source_url"].startswith("https://science.nasa.gov/"))

    def test_router_detects_single_compare_and_all_fact_intents(self):
        router = ScoutIntentRouter(load_planets())
        self.assertEqual(router.route("Tell me about Jupiter")["intent"], "planet_facts")
        self.assertEqual(router.route("Compare Earth and Mars")["intent"], "compare_planets")
        self.assertEqual(router.route("Give me facts about all planets")["intent"], "all_planet_facts")

    def test_sun_and_moon_each_have_twelve_facts_and_are_question_targets(self):
        bodies = load_solar_bodies()
        self.assertEqual({body["name"] for body in bodies}, {"Sun", "Moon"})
        for body in bodies:
            self.assertEqual(set(body["facts"]), set(FACT_KEYS), body["name"])
            self.assertEqual(len(body["facts"]), 12, body["name"])
            self.assertTrue(body["source_url"].startswith("https://science.nasa.gov/"))

        router = ScoutIntentRouter(load_planets(), bodies)
        self.assertEqual(router.route("How does the Sun shine?")["planets"], ["Sun"])
        self.assertEqual(router.route("Tell me about the Moon")["planets"], ["Moon"])
        self.assertEqual(router.route("How far is Mercury from the Sun?")["planets"], ["Mercury"])
        self.assertEqual(len(router.route("List planets")["planets"]), 8)

    def test_sun_and_moon_answers_include_all_twelve_facts(self):
        agent = PlanetariumAgent(zetaris=OfflineDatabase(), meterless=OfflineModel())
        for name in ("Sun", "Moon"):
            answer = agent.answer(f"Tell me about the {name}")
            self.assertIn("Notable fact", answer)
            self.assertEqual(answer.count("\n- "), 12)

    def test_answers_work_without_zetaris_or_meterless(self):
        agent = PlanetariumAgent(zetaris=OfflineDatabase(), meterless=OfflineModel())
        answer = agent.answer("What is the atmosphere of Jupiter?")
        self.assertIn("Atmosphere", answer)
        self.assertIn("hydrogen and helium", answer)
        self.assertIn("science.nasa.gov/jupiter/facts/", answer)

    def test_broad_planet_question_returns_all_twelve_facts(self):
        agent = PlanetariumAgent(zetaris=OfflineDatabase(), meterless=OfflineModel())
        answer = agent.answer("Tell me about Jupiter")
        self.assertIn("Atmosphere", answer)
        self.assertIn("Notable fact", answer)
        self.assertIn("Mean distance from the Sun", answer)

    def test_unknown_question_asks_for_planetarium_scope(self):
        agent = PlanetariumAgent(zetaris=OfflineDatabase(), meterless=OfflineModel())
        self.assertIn("Ask about a planet", agent.answer("Tell me a joke"))


class VercelEntrypointTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, method, path, body=b""):
        events = [{"type": "http.request", "body": body, "more_body": False}]
        responses = []

        async def receive():
            return events.pop(0)

        async def send(message):
            responses.append(message)

        await app(
            {"type": "http", "method": method, "path": path},
            receive,
            send,
        )
        status = responses[0]["status"]
        response_body = responses[1]["body"]
        return status, response_body

    async def test_homepage_and_catalog_routes(self):
        status, body = await self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Welcome, curious explorer", body)

        status, body = await self.request("GET", "/api/catalog")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["bodies"]), 10)

    async def test_question_route_and_invalid_request(self):
        status, body = await self.request(
            "POST",
            "/api/ask",
            json.dumps({"question": "Tell me about the Sun"}).encode("utf-8"),
        )
        self.assertEqual(status, 200)
        self.assertIn("Notable fact", json.loads(body)["answer"])

        status, _ = await self.request("POST", "/api/ask", b"not json")
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()