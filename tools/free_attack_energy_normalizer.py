"""Normalize printed attack Energy symbols in the bundled English card snapshot.

The literal token "Free" is a zero-Energy glyph sentinel in two known records.
Keep the immutable source card text/data and normalize at the consumer boundary.
"""


def normalized_attack_cost(attack: dict) -> tuple[str, ...]:
    """Return actual printed Energy requirements, excluding the zero-cost glyph."""
    cost = tuple(attack["cost"])
    return () if cost == ("Free",) else cost


def normalized_converted_energy_cost(attack: dict) -> int:
    """Count required Energy symbols before field effects modify attack costs."""
    return len(normalized_attack_cost(attack))
