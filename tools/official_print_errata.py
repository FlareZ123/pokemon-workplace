from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    has_tournament_ban_rule,
    load_json,
)

OFFICIAL_ERRATA_SOURCE = "https://play.pokemon.com/en-us/resources/documents/tcg-errata/"


@dataclass(frozen=True)
class PrintErrataEntry:
    name: str
    set_id: str
    material_overlay: bool
    note: str


PRINT_SPECIFIC_ERRATA: dict[str, PrintErrataEntry] = {
    "dp2-123": PrintErrataEntry("Magmortar LV.X", "dp2", False, "Flame Bluster Energy requirement"),
    "dp2-20": PrintErrataEntry("Ariados", "dp2", False, "Sticky Retreat Cost modifier"),
    "dp2-24": PrintErrataEntry("Exeggutor", "dp2", False, "String Bomb Basic Energy counting"),
    "dp2-28": PrintErrataEntry("Manectric", "dp2", False, "Lightning Twister Basic Energy counting"),
    "dp2-2": PrintErrataEntry("Alakazam", "dp2", True, "Psychic Guard Stage 2 scope"),
    "dp2-25": PrintErrataEntry("Glalie", "dp2", True, "Craggy Face damage calculation timing and Stage 2 scope"),
    "dp3-4": PrintErrataEntry("Entei", "dp3", False, "Blaze Roar Energy discard"),
    "dp3-25": PrintErrataEntry("Electivire", "dp3", False, "Discharge Energy discard and coin count"),
    "dp3-23": PrintErrataEntry("Banette", "dp3", False, "Ghost Head self-damage cap"),
    "dp3-26": PrintErrataEntry("Electrode", "dp3", False, "Energy Shift attachment semantics"),
    "dp3-42": PrintErrataEntry("Wormadam Sandy Cloak", "dp3", True, "Sandy Cloak opponent-only effect immunity"),
    "dp3-2": PrintErrataEntry("Blastoise", "dp3", True, "Waterlog Basic Energy type restriction"),
    "dp4-10": PrintErrataEntry("Tangrowth", "dp4", False, "Power Whip Basic Energy counting"),
    "dp4-57": PrintErrataEntry("Unown [G]", "dp4", False, "GUARD opponent-only effect immunity"),
    "dp6-79": PrintErrataEntry("Unown [V]", "dp6", False, "VACATION optional use and turn ending"),
    "dp7-18": PrintErrataEntry("Gengar", "dp7", True, "Fainting Spell Knocks Out the Attacking Pokémon"),
    "dp7-23": PrintErrataEntry("Roserade", "dp7", True, "Hidden Poison affects the Attacking Pokémon"),
    "dp7-26": PrintErrataEntry("Skuntank", "dp7", True, "Evolutionary Gas Active-position expiry"),
    "dp7-27": PrintErrataEntry("Staraptor", "dp7", True, "Protect Wing Stage 2 scope"),
    "pl1-126": PrintErrataEntry("Shaymin LV.X", "pl1", True, "Seed Flare may attach any Energy cards"),
    "pl1-23": PrintErrataEntry("Dialga", "pl1", False, "Metal-type card template"),
    "pl4-88": PrintErrataEntry("Lucky Egg", "pl4", True, "Draw requires the Knocked Out Pokémon to reach discard"),
    "hgss2-56": PrintErrataEntry("Onix", "hgss2", False, "Energy Healer only triggers from hand attachments"),
    "hgss3-72": PrintErrataEntry("Defender", "hgss3", True, "Damage reduction includes attacks not made by the opponent"),
    "hgss4-51": PrintErrataEntry("Unown", "hgss4", True, "CURE is optional"),
    "dv1-18": PrintErrataEntry("Exp. Share", "dv1", False, "Missing Pokémon Tool rule box"),
    "bw8-136": PrintErrataEntry("Charizard", "bw8", False, "Scorching Fire attack cost"),
    "xy3-90": PrintErrataEntry("Fighting Stadium", "xy3", True, "Damage bonus applies to the opponent's Active Pokémon-EX"),
    "xy4-98": PrintErrataEntry("Jamming Net Team Flare Hyper Gear", "xy4", True, "Damage reduction applies only to the attacking Pokémon's opponent"),
    "xy5-143": PrintErrataEntry("Shield Energy", "xy5", True, "Attachment scope and post-Weakness/Resistance damage reduction"),
    "xy11-42": PrintErrataEntry("Galvantula", "xy11", True, "Double Thread targets Benched Pokémon only"),
    "xy12-40": PrintErrataEntry("Electrode", "xy12", True, "Buzzap Thunder can attach to any Pokémon"),
    "sm5-120": PrintErrataEntry("Cyrus ◇", "sm5", False, "Active Pokémon requirement"),
    "sm12-1": PrintErrataEntry("Venusaur & Snivy-GX", "sm12", True, "Shining Vine can trigger for every qualifying attachment"),
    "sm12-210": PrintErrataEntry("Venusaur & Snivy-GX", "sm12", True, "Shining Vine can trigger for every qualifying attachment"),
    "sm12-249": PrintErrataEntry("Venusaur & Snivy-GX", "sm12", True, "Shining Vine can trigger for every qualifying attachment"),
    "smp-SM229": PrintErrataEntry("Venusaur & Snivy-GX", "smp", True, "Shining Vine can trigger for every qualifying attachment"),
    "swsh1-36": PrintErrataEntry("Cinderace", "swsh1", True, "Retreat Cost is one Colorless Energy"),
    "swsh9-109": PrintErrataEntry("Garchomp", "swsh9", False, "Sonic Slip protects only from the opponent's attacks"),
    "sv4-99": PrintErrataEntry("Minior", "sv4", True, "Far-Flying Meteor can trigger for every qualifying attachment"),
    "sv4-201": PrintErrataEntry("Minior", "sv4", True, "Far-Flying Meteor can trigger for every qualifying attachment"),
}

MATERIAL_OVERLAY_IDS = frozenset(
    card_id for card_id, entry in PRINT_SPECIFIC_ERRATA.items() if entry.material_overlay
)


def _replace_attack(card: dict[str, Any], attack_name: str, **updates: Any) -> None:
    for attack in card.get("attacks") or []:
        if attack.get("name") == attack_name:
            attack.update(updates)
            return
    raise ValueError(f"Attack {attack_name!r} not found on {card['id']}")


def _replace_ability(card: dict[str, Any], ability_name: str, text: str) -> None:
    for ability in card.get("abilities") or []:
        if ability.get("name") == ability_name:
            ability["text"] = text
            return
    raise ValueError(f"Ability {ability_name!r} not found on {card['id']}")


def normalize_print_specific_errata(card: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with material official print-specific errata applied."""

    normalized = deepcopy(card)
    card_id = normalized.get("id")

    if card_id == "dp2-2":
        _replace_attack(
            normalized,
            "Psychic Guard",
            text=(
                "During your opponent's next turn, any damage done to Alakazam by attacks from "
                "your opponent's Stage 2 Pokémon is reduced by 30 (after applying Weakness and Resistance)."
            ),
        )
    elif card_id == "dp2-25":
        _replace_ability(
            normalized,
            "Craggy Face",
            "As long as Glalie is your Active Pokémon, any damage done by attacks from your opponent's "
            "Stage 2 Pokémon is reduced by 20 (after applying Weakness and Resistance).",
        )
    elif card_id == "dp3-42":
        _replace_ability(
            normalized,
            "Sandy Cloak",
            "Prevent all effects of attacks, excluding damage, done to Wormadam Sandy Cloak by your opponent's Pokémon.",
        )
    elif card_id == "dp3-2":
        _replace_ability(
            normalized,
            "Waterlog",
            "Once during your turn (before your attack), you may use this power. If you do, your turn ends. "
            "Attach as many basic Energy cards from your hand to any of your Pokémon in any way you like. "
            "This power can't be used if Blastoise is affected by a Special Condition.",
        )
    elif card_id == "dp7-18":
        _replace_ability(
            normalized,
            "Fainting Spell",
            "Once during your opponent's turn, if Gengar would be Knocked Out by damage from an attack, "
            "you may flip a coin. If heads, the Attacking Pokémon is Knocked Out.",
        )
    elif card_id == "dp7-23":
        _replace_ability(
            normalized,
            "Hidden Poison",
            "If Roserade is your Active Pokémon and is damaged by an opponent's attack "
            "(even if Roserade is Knocked Out), the Attacking Pokémon is now Poisoned.",
        )
    elif card_id == "dp7-26":
        _replace_ability(
            normalized,
            "Evolutionary Gas",
            "Once during your turn (before your attack), when you play Skuntank from your hand to evolve 1 of "
            "your Active Pokémon, you may choose 1 of the Defending Pokémon. If that Pokémon tries to attack "
            "during your opponent's next turn, that attack does nothing. (If the Defending Pokémon is no longer "
            "your opponent's Active Pokémon, this effect ends.)",
        )
    elif card_id == "dp7-27":
        _replace_ability(
            normalized,
            "Protect Wing",
            "As long as Staraptor is your Active Pokémon, any damage done by attacks from your opponent's "
            "Stage 2 Pokémon is reduced by 20 (after applying Weakness and Resistance).",
        )
    elif card_id == "pl1-126":
        _replace_attack(
            normalized,
            "Seed Flare",
            text=(
                "Choose as many Energy cards from your hand as you like and attach them to your Pokémon in any "
                "way you like. If you do, this attack does 40 damage plus 20 more damage for each Grass Energy "
                "card attached in this way."
            ),
        )
    elif card_id == "pl4-88":
        normalized["rules"] = [
            "Attach Lucky Egg to 1 of your Pokémon that doesn't already have a Pokémon Tool attached to it. "
            "If that Pokémon is Knocked Out, discard this card.",
            "When the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack and "
            "put into your discard pile, draw cards until you have 7 cards in your hand.",
        ]
    elif card_id == "hgss3-72":
        normalized["rules"] = [
            "Attach Defender to 1 of your Pokémon. Discard this card at the end of your opponent's next turn. "
            "Any damage done to the Pokémon Defender is attached to by attacks is reduced by 20 "
            "(after applying Weakness and Resistance)."
        ]
    elif card_id == "hgss4-51":
        _replace_ability(
            normalized,
            "CURE",
            "Once during your turn, when you put Unown from your hand onto your Bench, you may remove all "
            "Special Conditions from your Active Pokémon.",
        )
    elif card_id == "xy3-90":
        normalized["rules"][0] = (
            "The attacks of each Fighting Pokémon in play (both yours and your opponent's) do 20 more damage "
            "to the opponent's Active Pokémon-EX (before applying Weakness and Resistance)."
        )
    elif card_id == "xy4-98":
        normalized["rules"][1] = (
            "The attacks of the Pokémon this card is attached to do 20 less damage to each of the opponent's "
            "Pokémon (before applying Weakness and Resistance). (Don't apply Weakness and Resistance for "
            "Benched Pokémon.)"
        )
    elif card_id == "xy5-143":
        normalized["rules"] = [
            "This card can only be attached to Pokémon. This card provides Metal Energy only while this card "
            "is attached to a Pokémon.",
            "Any damage done to the Metal Pokémon this card is attached to by an opponent's attack is reduced "
            "by 10 (after applying Weakness and Resistance).",
            "(If this card is attached to anything other than a Pokémon, discard this card.)",
        ]
    elif card_id == "xy11-42":
        _replace_attack(
            normalized,
            "Double Thread",
            text="This attack does 30 damage to 2 of your opponent's Benched Pokémon. Apply Weakness and Resistance.",
        )
    elif card_id == "xy12-40":
        _replace_ability(
            normalized,
            "Buzzap Thunder",
            "Once during your turn (before your attack), you may Knock Out this Pokémon and attach it to one of "
            "your Pokémon as a Special Energy card. This card provides 2 Lightning Energy only while this card "
            "is attached to a Pokémon.",
        )
    elif card_id in {"sm12-1", "sm12-210", "sm12-249", "smp-SM229"}:
        _replace_ability(
            normalized,
            "Shining Vine",
            "During your turn, if this Pokémon is your Active Pokémon, whenever you attach a Grass Energy card "
            "from your hand to it, you may switch 1 of your opponent's Benched Pokémon with their Active Pokémon.",
        )
    elif card_id == "swsh1-36":
        normalized["retreatCost"] = ["Colorless"]
        normalized["convertedRetreatCost"] = 1
    elif card_id in {"sv4-99", "sv4-201"}:
        _replace_ability(
            normalized,
            "Far-Flying Meteor",
            "During your turn, if this Pokémon is on your Bench, whenever you attach an Energy card from your "
            "hand to this Pokémon, you may switch it with your Active Pokémon.",
        )

    return normalized


def _load_cards(resources_root: Path) -> tuple[frozenset[str], dict[str, dict[str, Any]]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = frozenset(
        row["id"] for row in sets if (row.get("legalities") or {}).get("expanded") == "Legal"
    )
    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards_by_id[card["id"]] = card
    return expanded_sets, cards_by_id


def summarize_print_specific_errata(resources_root: Path) -> dict[str, Any]:
    expanded_sets, cards_by_id = _load_cards(resources_root)

    missing = sorted(set(PRINT_SPECIFIC_ERRATA) - set(cards_by_id))
    if missing:
        raise ValueError(f"Official print-specific errata IDs missing from database: {missing}")

    identity_mismatches = []
    for card_id, entry in PRINT_SPECIFIC_ERRATA.items():
        card = cards_by_id[card_id]
        if card.get("name") != entry.name or card.get("_set_id") != entry.set_id:
            identity_mismatches.append(
                {
                    "id": card_id,
                    "expected_name": entry.name,
                    "actual_name": card.get("name"),
                    "expected_set_id": entry.set_id,
                    "actual_set_id": card.get("_set_id"),
                }
            )
    if identity_mismatches:
        raise ValueError(f"Official errata identity mismatch: {identity_mismatches}")

    changed_ids = []
    for card_id in sorted(PRINT_SPECIFIC_ERRATA):
        card = cards_by_id[card_id]
        normalized = normalize_print_specific_errata(card)
        changed = gameplay_fingerprint(card) != gameplay_fingerprint(normalized)
        expected_changed = PRINT_SPECIFIC_ERRATA[card_id].material_overlay
        if changed != expected_changed:
            raise ValueError(
                f"Material overlay expectation mismatch for {card_id}: changed={changed}, expected={expected_changed}"
            )
        if changed:
            changed_ids.append(card_id)

    legal_cards = [
        card
        for card in cards_by_id.values()
        if card["_set_id"] in expanded_sets and classify_effective_legality(card)[0] == "Legal"
    ]
    raw_legal_fingerprints = defaultdict(list)
    normalized_legal_fingerprints = defaultdict(list)
    for card in legal_cards:
        raw_legal_fingerprints[gameplay_fingerprint(card)].append(card)
        normalized_legal_fingerprints[gameplay_fingerprint(normalize_print_specific_errata(card))].append(card)

    raw_exact_candidates = []
    normalized_exact_candidates = []
    for card in cards_by_id.values():
        if card["_set_id"] in expanded_sets:
            continue
        if has_tournament_ban_rule(card) or (card.get("legalities") or {}).get("unlimited") == "Banned":
            continue
        if gameplay_fingerprint(card) in raw_legal_fingerprints:
            raw_exact_candidates.append(card["id"])
        if gameplay_fingerprint(normalize_print_specific_errata(card)) in normalized_legal_fingerprints:
            normalized_exact_candidates.append(card["id"])

    expanded_changed = [card_id for card_id in changed_ids if cards_by_id[card_id]["_set_id"] in expanded_sets]
    historical_changed = [card_id for card_id in changed_ids if cards_by_id[card_id]["_set_id"] not in expanded_sets]

    return {
        "source": OFFICIAL_ERRATA_SOURCE,
        "counts": {
            "official_print_specific_prints": len(PRINT_SPECIFIC_ERRATA),
            "material_database_overlays": len(changed_ids),
            "material_expanded_prints": len(expanded_changed),
            "material_historical_prints": len(historical_changed),
            "already_semantically_reflected_or_metadata_only": len(PRINT_SPECIFIC_ERRATA) - len(changed_ids),
            "raw_legal_gameplay_fingerprints": len(raw_legal_fingerprints),
            "normalized_legal_gameplay_fingerprints": len(normalized_legal_fingerprints),
            "raw_exact_reprint_candidates": len(raw_exact_candidates),
            "normalized_exact_reprint_candidates": len(normalized_exact_candidates),
        },
        "material_expanded_ids": expanded_changed,
        "material_historical_ids": historical_changed,
        "raw_exact_candidate_ids": sorted(raw_exact_candidates),
        "normalized_exact_candidate_ids": sorted(normalized_exact_candidates),
        "entries": {
            card_id: {
                "name": PRINT_SPECIFIC_ERRATA[card_id].name,
                "set_id": PRINT_SPECIFIC_ERRATA[card_id].set_id,
                "material_overlay": PRINT_SPECIFIC_ERRATA[card_id].material_overlay,
                "note": PRINT_SPECIFIC_ERRATA[card_id].note,
                "in_expanded_set": cards_by_id[card_id]["_set_id"] in expanded_sets,
                "raw_fingerprint": gameplay_fingerprint(cards_by_id[card_id]),
                "normalized_fingerprint": gameplay_fingerprint(
                    normalize_print_specific_errata(cards_by_id[card_id])
                ),
            }
            for card_id in sorted(PRINT_SPECIFIC_ERRATA)
        },
    }
