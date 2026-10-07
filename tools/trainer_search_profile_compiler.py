"""Compile conservative multi-output Trainer text into search profiles.

The compiler covers the literal fixed-axis and conditional-additional classes
from multi_output_search_catalog.py. It preserves state predicates as metadata
instead of deciding whether a card is strategically playable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from multi_output_search_catalog import catalog_multi_output_trainers


@dataclass(frozen=True)
class SearchOutput:
    """One abstract search-output channel."""

    label: str
    max_units: int | None = 1


@dataclass(frozen=True)
class CompiledTrainerSearchProfile:
    """Conservative output and cost metadata for one Trainer print."""

    card_id: str
    name: str
    action_class: str
    base_outputs: tuple[SearchOutput, ...]
    conditional_outputs: tuple[SearchOutput, ...] = ()
    required_discard_other_cards: int = 0
    optional_discard_other_cards: int = 0
    discards_entire_hand: bool = False
    play_condition: str | None = None


_ARTICLE_RE = re.compile(r"^(?:a|an)\s+", re.IGNORECASE)
_UP_TO_RE = re.compile(r"^up to\s+(\d+)\s+(.+)$", re.IGNORECASE)
_ANY_NUMBER_RE = re.compile(
    r"^any number of\s+(.+)$",
    re.IGNORECASE,
)
_REQUIRED_DISCARD_RE = re.compile(
    r"only if you discard\s+(\d+)\s+other cards",
    re.IGNORECASE,
)
_OPTIONAL_DISCARD_RE = re.compile(
    r"may discard\s+(\d+)\s+other cards",
    re.IGNORECASE,
)


def _singularize_card_label(label: str) -> str:
    if label.lower().endswith(" cards"):
        return label[:-1]
    return label


def _clean_clause(clause: str) -> str:
    clause = re.sub(
        r"\s+in this way\.?$",
        "",
        clause.strip(),
        flags=re.IGNORECASE,
    )
    return clause.rstrip(".").strip()


def _split_axes(clause: str) -> tuple[str, ...]:
    """Split coordinated article-led axes without semantic normalization."""

    cleaned = _clean_clause(clause)
    pieces = re.split(
        r",\s*(?:and\s+)?|\s+and\s+",
        cleaned,
    )
    return tuple(
        _ARTICLE_RE.sub("", piece.strip())
        for piece in pieces
        if piece.strip()
    )


def _parse_output_clause(clause: str) -> tuple[SearchOutput, ...]:
    cleaned = _clean_clause(clause)

    up_to = _UP_TO_RE.match(cleaned)
    if up_to is not None:
        units = int(up_to.group(1))
        label = _singularize_card_label(
            _ARTICLE_RE.sub("", up_to.group(2).strip())
        )
        return (SearchOutput(label, units),)

    any_number = _ANY_NUMBER_RE.match(cleaned)
    if any_number is not None:
        label = _singularize_card_label(
            _ARTICLE_RE.sub("", any_number.group(1).strip())
        )
        return (SearchOutput(label, None),)

    axes = _split_axes(cleaned)
    return tuple(
        SearchOutput(_singularize_card_label(axis), 1)
        for axis in axes
    )


def _first_search_clause(text: str) -> str | None:
    match = re.search(
        r"search your deck for\s+(.*?)(?:,\s*reveal|\.\s*Then|\.\s*Shuffle)",
        text,
        re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group(1).strip()


def _conditional_search_clause(text: str) -> str | None:
    match = re.search(
        r"may also search for\s+(.*?)(?:\.|$)",
        text,
        re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group(1).strip()


def _action_class(subtypes: list[str]) -> str:
    for candidate in ("Item", "Supporter", "Stadium", "Pokémon Tool"):
        if candidate in subtypes:
            return candidate
    return subtypes[0] if subtypes else "Trainer"


def compile_multi_output_trainer_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[CompiledTrainerSearchProfile, ...]:
    """Compile fixed-axis and conditional-additional Trainer search profiles."""

    catalog = catalog_multi_output_trainers(resources_root)
    profiles: list[CompiledTrainerSearchProfile] = []

    for row in catalog["rows"]:
        classes = set(row["classifications"])
        if not (
            "fixed_axes" in classes
            or "conditional_additional" in classes
        ):
            continue

        rules = list(row["rules"])
        text = " ".join(rules)
        base_clause = _first_search_clause(text)
        if base_clause is None:
            raise ValueError(
                f"Could not parse base search clause for {row['id']}"
            )

        conditional_clause = _conditional_search_clause(text)
        optional_discard = 0
        if conditional_clause is not None:
            optional_match = _OPTIONAL_DISCARD_RE.search(text)
            if optional_match is None:
                raise ValueError(
                    f"Conditional additional search has no parsed discard cost: {row['id']}"
                )
            optional_discard = int(optional_match.group(1))

        required_match = _REQUIRED_DISCARD_RE.search(text)
        required_discard = (
            int(required_match.group(1))
            if required_match is not None
            else 0
        )

        play_condition = next(
            (
                rule
                for rule in rules
                if rule.lower().startswith(
                    "you can play this card only if"
                )
            ),
            None,
        )

        profiles.append(
            CompiledTrainerSearchProfile(
                card_id=row["id"],
                name=row["name"],
                action_class=_action_class(list(row["subtypes"])),
                base_outputs=_parse_output_clause(base_clause),
                conditional_outputs=(
                    _parse_output_clause(conditional_clause)
                    if conditional_clause is not None
                    else ()
                ),
                required_discard_other_cards=required_discard,
                optional_discard_other_cards=optional_discard,
                discards_entire_hand=(
                    "discard your hand and search your deck"
                    in text.lower()
                ),
                play_condition=play_condition,
            )
        )

    return tuple(profiles)
