"""Compile the order of paired own/opponent switch effects for four gust cards.

This is a deliberately audited subset of the current-semantic Trainer catalog.
It preserves the first action and the conditional follow-on action, because
the second half of 'If you do' requires first-half success.
"""
from dataclasses import dataclass
from pathlib import Path

from tools.trainer_gust_catalog import catalog


@dataclass(frozen=True)
class PairedSwitchProgram:
    name: str
    first: str
    second: str
    copies_together: int = 1
    team_rocket_own_only: bool = False


PROGRAMS = {
    "Prime Catcher": PairedSwitchProgram("Prime Catcher", "opponent", "own"),
    "Cross Switcher": PairedSwitchProgram("Cross Switcher", "opponent", "own", 2),
    "Guzma": PairedSwitchProgram("Guzma", "opponent", "own"),
    "Team Rocket's Giovanni": PairedSwitchProgram(
        "Team Rocket's Giovanni", "own", "opponent",
        team_rocket_own_only=True
    ),
}


def compiled_profiles(resources_root: Path):
    """Return the covered effective-legal print records with programs."""
    return tuple(
        (row, PROGRAMS[row.card_name])
        for row in catalog(resources_root)
        if row.card_name in PROGRAMS
    )


def switch_effects(
    program: PairedSwitchProgram,
    own_bench_exists: bool,
    opponent_target_eligible: bool,
    own_active_is_team_rocket: bool = False,
    own_bench_has_team_rocket: bool = False,
) -> tuple[str, ...]:
    """Resolve the ordered first and conditional second switches.

    Inputs are already interpreted card/board eligibility predicates, not
    a physical board transition or a card playability validator.
    """
    can_own = (
        own_active_is_team_rocket and own_bench_has_team_rocket
        if program.team_rocket_own_only else own_bench_exists
    )
    can_opponent = opponent_target_eligible
    can_first = can_opponent if program.first == "opponent" else can_own
    if not can_first:
        return ()
    can_second = can_own if program.second == "own" else can_opponent
    return (program.first, program.second) if can_second else (program.first,)
