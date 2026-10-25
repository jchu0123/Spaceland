import unittest

from planetarium import FACT_KEYS, PlanetariumAgent, ScoutIntentRouter, load_planets


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


if __name__ == "__main__":
    unittest.main()