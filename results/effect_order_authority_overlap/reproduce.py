"""Reproduce overlap-safe effect-order authority behavior."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from effect_order_authority import OrderAuthorityCase, OrderAuthorityContext
from effect_order_authority_overlap import (
    AuthorityResolutionStatus,
    player_may_choose_order,
    resolve_overlapping_authority,
)


def main() -> None:
    # Player A is taking the turn. Player B owns the Knocked Out Reuniclus.
    split_context = OrderAuthorityContext(
        current_turn_player="A",
        next_turn_player="B",
        knocked_out_pokemon_owner="B",
    )

    multi_only = resolve_overlapping_authority(
        (OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,),
        split_context,
    )
    assert multi_only.status == AuthorityResolutionStatus.RESOLVED
    assert multi_only.chooser == "A"

    local_only = resolve_overlapping_authority(
        (OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,),
        split_context,
    )
    assert local_only.status == AuthorityResolutionStatus.RESOLVED
    assert local_only.chooser == "B"

    # The bundled rulebook and the official Lost City/Reuniclus ruling make
    # different authority claims if both scopes are asserted for this state.
    # No precedence is encoded because the current evidence does not establish
    # which scope overrides the other in their overlap.
    split_overlap = resolve_overlapping_authority(
        (
            OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
            OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,
        ),
        split_context,
    )
    assert split_overlap.status == AuthorityResolutionStatus.CONFLICT
    assert split_overlap.chooser is None
    assert {claim.chooser for claim in split_overlap.claims} == {"A", "B"}
    assert not player_may_choose_order(split_overlap, "A")
    assert not player_may_choose_order(split_overlap, "B")

    # If both authority roles happen to name the same physical player, the
    # concrete chooser is determinate even though rule precedence remains
    # unspecified.
    aligned_context = OrderAuthorityContext(
        current_turn_player="A",
        next_turn_player="B",
        knocked_out_pokemon_owner="A",
    )
    aligned_overlap = resolve_overlapping_authority(
        (
            OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
            OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,
        ),
        aligned_context,
    )
    assert aligned_overlap.status == AuthorityResolutionStatus.RESOLVED
    assert aligned_overlap.chooser == "A"
    assert player_may_choose_order(aligned_overlap, "A")
    assert not player_may_choose_order(aligned_overlap, "B")

    missing_owner = OrderAuthorityContext(
        current_turn_player="A",
        next_turn_player="B",
    )
    missing = resolve_overlapping_authority(
        (OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,),
        missing_owner,
    )
    assert missing.status == AuthorityResolutionStatus.MISSING_CONTEXT
    assert missing.chooser is None

    for invalid in ((), (
        OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
        OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
    )):
        try:
            resolve_overlapping_authority(invalid, split_context)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid authority case set should fail")

    print("Effect-order authority overlap regressions passed")


if __name__ == "__main__":
    main()
