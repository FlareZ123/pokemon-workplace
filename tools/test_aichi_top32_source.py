"""Standalone regression: python tools/test_aichi_top32_source.py"""
import unittest

from aichi_top32_source import parse_source


class TournamentSourceParserTest(unittest.TestCase):
    def setUp(self):
        self.html = """<html><span>10th May 2026 • 926 Players</span><h3>1st Player One</h3><span>Control</span>
        <h4>Pokémon (4)</h4><a>4 Iron Thorns ex</a><a>$1.99</a>
        <h4>Trainer (48)</h4><a>48 Example Trainer</a>
        <h4>Energy (8)</h4><a>8 Special Energy</a>
        <button>Copy to Clipboard</button>
        <h3>2nd Player Two</h3><span>Combo</span>
        <h4>Pokémon (8)</h4><a>4 Pokemon A</a><a>4 Pokemon B</a>
        <h4>Trainer (41)</h4><a>41 Example Trainer</a>
        <h4>Energy (11)</h4><a>11 Basic Psychic Energy</a></html>"""

    def test_two_source_rows(self):
        decks = parse_source(self.html)
        self.assertEqual(len(decks), 2)
        self.assertEqual(decks[0]["player"], "Player One")
        self.assertEqual(decks[0]["archetype"], "Control")
        self.assertEqual(decks[0]["pokemon"], [{"count": 4, "name": "Iron Thorns ex"}])
        self.assertEqual(decks[1]["energy"], [{"count": 11, "name": "Basic Psychic Energy"}])

    def test_split_card_count_nodes(self):
        page = self.html.replace(
            "<a>4 Iron Thorns ex</a>",
            "<span>4</span><a>Iron Thorns ex</a>",
        ).replace(
            "<a>48 Example Trainer</a>",
            "<span>48</span><a>Example Trainer</a>",
        ).replace(
            "<a>8 Special Energy</a>",
            "<span>8</span><a>Special Energy</a>",
        )
        decks = parse_source(page)
        self.assertEqual(decks[0]["pokemon"], [{"count": 4, "name": "Iron Thorns ex"}])
        self.assertEqual(decks[0]["declared"], {"pokemon": 4, "trainer": 48, "energy": 8})

    def test_separate_same_name_rows_preserved(self):
        page = self.html.replace(
            "<a>4 Pokemon A</a><a>4 Pokemon B</a>",
            "<span>4</span><a>Pokemon A</a>"
            "<span>2</span><a>Pokemon B</a>"
            "<span>2</span><a>Pokemon B</a>",
        )
        decks = parse_source(page)
        self.assertEqual(decks[1]["pokemon"], [
            {"count": 4, "name": "Pokemon A"},
            {"count": 2, "name": "Pokemon B"},
            {"count": 2, "name": "Pokemon B"},
        ])

    def test_incomplete_category_rejected(self):
        with self.assertRaisesRegex(ValueError, "declared 48, parsed 47"):
            parse_source(self.html.replace("48 Example Trainer", "47 Example Trainer"))

    def test_missing_archetype_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing archetype"):
            parse_source(self.html.replace("<span>Control</span>", ""))

    def test_duplicate_placement_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate placing"):
            parse_source(self.html.replace("2nd Player Two", "1st Player Two"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
