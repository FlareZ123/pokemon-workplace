"""Conservative current-semantic Trainer gust catalog for English Expanded snapshot.

Finds all Expanded-set, nonbanned Trainer prints whose literal rules mention
both 'switch' and 'opponent'. A hand-audited name table marks target choice and
source constraints; unknown names remain explicitly unclassified.

IMPORTANT: official Pokemon Catcher errata supersedes the printed pre-flip
effect in three bundled BW cards. See official Pokemon TCG Errata:
https://assets.pokemon.com/assets/cms/pdf/tcg/tcg_errata.pdf (page 1).
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import json

from tools.build_expanded_legality_baseline import classify_effective_legality


@dataclass(frozen=True)
class GustProfile:
    family: str
    target_scope: str
    gates: tuple[str, ...] = ()

    @property
    def player_selects_existing_bench(self) -> bool:
        return self.family == "player_targeted_existing_bench"


UNRESTRICTED = GustProfile("player_targeted_existing_bench", "any")
CATEGORIES: dict[str, GustProfile] = {
    "Boss's Orders": GustProfile("player_targeted_existing_bench", "any", ("supporter",)),
    "Boss's Orders (Ghetsis)": GustProfile("player_targeted_existing_bench", "any", ("supporter",)),
    "Lysandre": GustProfile("player_targeted_existing_bench", "any", ("supporter",)),
    "Counter Catcher": GustProfile(
        "player_targeted_existing_bench", "any", ("own_prizes_gt_opponent",)
    ),
    "Cross Switcher": GustProfile(
        "player_targeted_existing_bench", "any", ("two_copies_together", "own_switch")
    ),
    "Custom Catcher": GustProfile(
        "player_targeted_existing_bench", "any", ("two_copies_for_gust", "draw_alternative")
    ),
    "Great Catcher": GustProfile(
        "player_targeted_existing_bench", "gx_or_legacy_ex", ("discard_two",)
    ),
    "Guzma": GustProfile(
        "player_targeted_existing_bench", "any", ("supporter", "own_switch")
    ),
    "Lisia's Appeal": GustProfile(
        "player_targeted_existing_bench", "basic", ("supporter", "confuse_target")
    ),
    "Mega Catcher": GustProfile(
        "player_targeted_existing_bench", "mega_evolution"
    ),
    "Pokémon Catcher": GustProfile(
        "player_targeted_existing_bench", "any", ("fair_coin",)
    ),
    "Prime Catcher": GustProfile(
        "player_targeted_existing_bench", "any", ("ace_spec", "own_switch")
    ),
    "Serena": GustProfile(
        "player_targeted_existing_bench", "pokemon_v_family", ("supporter", "draw_alternative")
    ),
    "Shauntal": GustProfile(
        "player_targeted_existing_bench", "any", ("supporter", "fair_coin", "tails_own_switch")
    ),
    "Team Rocket's Giovanni": GustProfile(
        "player_targeted_existing_bench", "any",
        ("supporter", "must_switch_own_team_rocket_first")
    ),
    "Toy Catcher": GustProfile(
        "player_targeted_existing_bench", "remaining_hp_le_50"
    ),
    "Erika's Invitation": GustProfile(
        "opponent_hand_to_bench_then_active", "opponent_hand_basic", ("supporter",)
    ),
    "Escape Rope": GustProfile(
        "opponent_chooses_promotion", "any", ("both_players_switch",)
    ),
    "Repel": GustProfile("opponent_chooses_promotion", "any"),
    "Ryme": GustProfile(
        "opponent_chooses_promotion", "any", ("supporter", "draw_three")
    ),
    "Kieran": GustProfile("no_opponent_switch", "none", ("supporter",)),
    "Team Rocket's Bother-Bot": GustProfile(
        "non_pokemon_zone_swap", "none", ("opponent_prize_hand_exchange",)
    ),
}

# Known card IDs with an obsolete, deterministic literal effect in the bundled
# archive. All are played with the current coin-flip errata instead.
OLD_NO_FLIP_PRINT_IDS = frozenset({"bw2-95", "bw5-111", "bw10-83"})
CORRECTED_POKEMON_CATCHER_EFFECT = (
    "Flip a coin. If heads, switch 1 of your opponent's Benched Pokémon "
    "with their Active Pokémon."
)


@dataclass(frozen=True)
class GustPrint:
    card_id: str
    card_name: str
    subtype: tuple[str, ...]
    raw_text: str
    effective_text: str
    profile: GustProfile
    errata_applied: bool


def catalog(resources_root: Path) -> tuple[GustPrint, ...]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    rows: list[GustPrint] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if card.get("supertype") != "Trainer":
                continue
            if classify_effective_legality(card)[0] == "Banned":
                continue
            rules = card.get("rules") or []
            raw = " ".join(" ".join(rule.split()) for rule in rules)
            if "opponent" not in raw.lower() or "switch" not in raw.lower():
                continue
            name = card["name"]
            profile = CATEGORIES.get(name, GustProfile("unclassified", "unknown"))
            corrected = card["id"] in OLD_NO_FLIP_PRINT_IDS
            effective = (
                CORRECTED_POKEMON_CATCHER_EFFECT if corrected else raw
            )
            rows.append(GustPrint(
                card["id"], name, tuple(card.get("subtypes") or ()),
                raw, effective, profile, corrected
            ))
    return tuple(rows)


def summary(rows: tuple[GustPrint, ...]) -> dict:
    by_family = defaultdict(set)
    for row in rows:
        by_family[row.profile.family].add(row.card_name)
    return {
        "print_count": len(rows),
        "distinct_names": len({row.card_name for row in rows}),
        "family_names": {key: sorted(value) for key, value in sorted(by_family.items())},
        "errata_print_ids": sorted(
            row.card_id for row in rows if row.errata_applied
        ),
        "target_scopes": dict(sorted(Counter(
            row.profile.target_scope
            for row in rows if row.profile.player_selects_existing_bench
        ).items())),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "resources"
    print(json.dumps(summary(catalog(root)), ensure_ascii=False, indent=2))
