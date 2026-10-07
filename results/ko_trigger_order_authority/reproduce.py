"""Reproduce source-scoped KO trigger-order authority claims."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    ASIA_LOST_CITY_REUNICLUS_QA,
    LOST_CITY_REUNICLUS,
    TPCI_FEB_2026,
    OrderingAuthority,
    OrderingContext,
    TimingWindow,
    TriggerKind,
    assess_ordering_authority,
)


def main() -> None:
    lost_city_context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_CITY_REUNICLUS,
    )

    tpci = assess_ordering_authority(
        lost_city_context,
        (TPCI_FEB_2026,),
    )
    assert tpci.resolved_authority == OrderingAuthority.CURRENT_PLAYER
    assert not tpci.has_conflict

    asia = assess_ordering_authority(
        lost_city_context,
        (ASIA_LOST_CITY_REUNICLUS_QA,),
    )
    assert (
        asia.resolved_authority
        == OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER
    )
    assert not asia.has_conflict

    japan = assess_ordering_authority(
        lost_city_context,
        (JAPAN_LOST_CITY_QA,),
    )
    assert (
        japan.resolved_authority
        == OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER
    )

    asia_japan = assess_ordering_authority(
        lost_city_context,
        (ASIA_LOST_CITY_REUNICLUS_QA, JAPAN_LOST_CITY_QA),
    )
    assert (
        asia_japan.resolved_authority
        == OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER
    )
    assert not asia_japan.has_conflict

    combined = assess_ordering_authority(
        lost_city_context,
        (
            TPCI_FEB_2026,
            ASIA_LOST_CITY_REUNICLUS_QA,
            JAPAN_LOST_CITY_QA,
        ),
    )
    assert combined.resolved_authority is None
    assert combined.has_conflict
    assert combined.authorities == {
        OrderingAuthority.CURRENT_PLAYER,
        OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER,
    }

    lost_out_context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_CITY_LOST_OUT,
    )
    japan_lost_out = assess_ordering_authority(
        lost_out_context,
        (JAPAN_LOST_CITY_QA,),
    )
    assert (
        japan_lost_out.resolved_authority
        == OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER
    )
    tpci_japan_lost_out = assess_ordering_authority(
        lost_out_context,
        (TPCI_FEB_2026, JAPAN_LOST_CITY_QA),
    )
    assert tpci_japan_lost_out.has_conflict

    # The local 2025 Advanced Player's Rulebook text only states a controller
    # for the narrower case where several Pokemon are Knocked Out together.
    legacy_single = assess_ordering_authority(
        lost_city_context,
        (ADVANCED_RULEBOOK_3_4,),
    )
    assert legacy_single.resolved_authority is None
    assert not legacy_single.claims

    legacy_multi = assess_ordering_authority(
        OrderingContext(
            timing_window=TimingWindow.DURING_TURN,
            trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
            simultaneous_knockout_count=2,
        ),
        (ADVANCED_RULEBOOK_3_4,),
    )
    assert legacy_multi.resolved_authority == OrderingAuthority.CURRENT_PLAYER

    checkup = assess_ordering_authority(
        OrderingContext(
            timing_window=TimingWindow.POKEMON_CHECKUP,
            trigger_kind=TriggerKind.OTHER,
        ),
        (TPCI_FEB_2026,),
    )
    assert checkup.resolved_authority == OrderingAuthority.NEXT_PLAYER

    print("KO trigger-order authority source regressions passed")


if __name__ == "__main__":
    main()
