"""Standalone tests for source-print reconciliation on a Windows Python runner."""
import copy
import hashlib
import unittest
from unittest.mock import patch

from aichi_source_print_map import BASELINE_ROW_COUNTS, audit_source


class SourcePrintMappingTest(unittest.TestCase):
    def setUp(self):
        self.cards = {
            "swsh6": [{"id":"swsh6-74","name":"Shadow Rider Calyrex V",
                       "number":"74","supertype":"Pokémon",
                       "legalities":{"expanded":"Legal"}}],
            "xy4": [{"id":"xy4-92","name":"Battle Compressor Team Flare Gear",
                     "number":"92","supertype":"Trainer",
                     "legalities":{"expanded":"Legal"}}],
            "sm9": [{"id":"sm9-51","name":"Tapu Koko ◇","number":"51",
                     "supertype":"Pokémon","legalities":{"expanded":"Legal"}}],
            "bw1": [{"id":"bw1-105","name":"Grass Energy","number":"105",
                     "supertype":"Energy","subtypes":["Basic"],
                     "legalities":{"expanded":"Legal"}}],
        }
        self.codes = {"CRE":["swsh6"],"PHF":["xy4"],"TEU":["sm9"],"BLW":["bw1"]}
        self.source = {
            "decks": [{"placing":1,"player":"Test","archetype":"Test",
                       "pokemon":[{"count":1,"name":"Shadow Rider Calyrex V"},
                                  {"count":1,"name":"Tapu Koko"}],
                       "trainer":[{"count":1,"name":"Battle Compressor"},
                                  {"count":1,"name":"Palace Book"}],
                       "energy":[{"count":1,"name":"Grass Energy"}]}]
        }
        self.html = (
            '<div class="decklist-card"><a href="/cards/CRE/74">1 Shadow Rider Calyrex V</a></div>'
            '<div class="decklist-card"><a href="/cards/TEU/51">1 Tapu Koko ♢</a></div>'
            '<div class="decklist-card"><a href="/cards/PHF/92">1 Battle Compressor</a></div>'
            '<div class="decklist-card"><a href="/cards/jp/SMP/NAN25?translate=en">'
            '1 Palace Book unreleased</a></div>'
            '<div class="decklist-card"><a href="/cards/MEE/9">1 Grass Energy</a></div>'
        )
        self.expected = {"exact_english_catalog":3,
                         "japanese_only":1,"basic_energy_surrogate":1}

    def run_audit(self, html=None, source=None):
        html = self.html if html is None else html
        source = copy.deepcopy(self.source if source is None else source)
        source["source_html_sha256"] = hashlib.sha256(self.html.encode()).hexdigest()
        with patch.dict(BASELINE_ROW_COUNTS,self.expected,clear=True):
            return audit_source(html,source,self.codes,self.cards)

    def test_alias_prism_promo_and_surrogate(self):
        report = self.run_audit()
        rows = [(c,r) for c in ("pokemon","trainer","energy")
                for r in report["decks"][0][c]]
        self.assertEqual([r["catalog_mapping_status"] for _,r in rows],
            ["exact_english_catalog","exact_english_catalog",
             "exact_english_catalog","japanese_only","basic_energy_surrogate"])
        self.assertEqual([r["catalog_card_id"] for _,r in rows],
            ["swsh6-74","sm9-51","xy4-92",None,"bw1-105"])
        self.assertEqual(report["print_mapping"]["physical_copy_status"],
            {"exact_english_catalog":3,"japanese_only":1,"basic_energy_surrogate":1})

    def test_hash_tamper_rejected(self):
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            self.run_audit(self.html.replace("Grass Energy","Water Energy"))

    def test_nonexistent_print_rejected(self):
        html = self.html.replace("/cards/CRE/74","/cards/CRE/999")
        source = copy.deepcopy(self.source)
        source["source_html_sha256"] = hashlib.sha256(html.encode()).hexdigest()
        with patch.dict(BASELINE_ROW_COUNTS,self.expected,clear=True):
            with self.assertRaisesRegex(ValueError,"English candidates"):
                audit_source(html,source,self.codes,self.cards)

    def test_missing_row_rejected(self):
        with self.assertRaisesRegex(ValueError,"Displayed card rows"):
            source = copy.deepcopy(self.source)
            source["decks"][0]["pokemon"].pop()
            self.run_audit(source=source)

    def test_duplicate_primary_link_rejected(self):
        html = self.html.replace(
            "1 Grass Energy</a>",
            '1 Grass Energy</a><a href="/cards/MEE/9">duplicate</a>',
        )
        source = copy.deepcopy(self.source)
        source["source_html_sha256"] = hashlib.sha256(html.encode()).hexdigest()
        with patch.dict(BASELINE_ROW_COUNTS,self.expected,clear=True):
            with self.assertRaisesRegex(ValueError,"one primary card anchor"):
                audit_source(html,source,self.codes,self.cards)


if __name__ == "__main__":
    unittest.main(verbosity=2)
