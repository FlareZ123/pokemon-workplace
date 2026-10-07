"""Reproduce growable KO membership with a Fainting Spell-like branch."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from cross_player_knockout_resolution import (
    choose_promotion,
    promotion_order,
    resolve_cross_player_knock_out,
)
from growing_knockout_context import (
    begin_growing_knock_out_context,
    mark_additional_knock_out,
    to_cross_player_context,
)
from identity_materialization import assert_conserved
from ko_cascade_text_catalog import build
from results.cross_player_knockout_resolution.reproduce import make_player


def main() -> None:
    catalog = build(ROOT / "resources")
    summary = catalog["summary"]
    assert summary["matched_prints"] == 14
    assert summary["matched_names"] == 11
    assert summary["prints_by_category"] == {
        "attacker_damage_counters": 7,
        "direct_attacker_ko": 7,
    }
    assert summary["database_text_typo_prints"] == 2

    rows = {row["card_id"]: row for row in catalog["rows"]}
    assert rows["me55-90"]["ability_name"] == "Fainting Spell"
    assert rows["xy4-43"]["category"] == "direct_attacker_ko"
    assert rows["sm1-47"]["category"] == "attacker_damage_counters"

    initial_a, state_a = make_player("a")
    initial_b, state_b = make_player("b")

    # A attacked during its turn, so B is the player whose turn would be next.
    # Initially only B's Active has been Knocked Out by the attack.
    growing = begin_growing_knock_out_context(
        {"A": state_a, "B": state_b},
        next_player_id="B",
        initial_knockouts={"B": ("b-active",)},
    )
    assert growing is not None
    assert growing.pending_for("A") == ()
    assert growing.pending_for("B") == ("b-active",)
    assert to_cross_player_context(growing) is None

    # A heads result on Fainting Spell-like text KOs the Attacking Pokemon.
    # The original pending member stays present while the other player's KO set
    # grows before the common disposal boundary.
    heads = mark_additional_knock_out(
        growing,
        player_id="A",
        pokemon_id="a-active",
    )
    assert heads is not None
    assert heads.pending_for("A") == ("a-active",)
    assert heads.pending_for("B") == ("b-active",)

    # Marking the same physical Pokemon twice is idempotent.
    assert (
        mark_additional_knock_out(
            heads,
            player_id="A",
            pokemon_id="a-active",
        )
        == heads
    )

    context = to_cross_player_context(heads)
    assert context is not None
    assert promotion_order(context) == ("B", "A")

    after_b = choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-bench",
    )
    assert after_b is not None
    ready = choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="a-bench",
    )
    assert ready is not None

    resolved = resolve_cross_player_knock_out(ready)
    assert resolved is not None
    final_a = resolved.state_for("A")
    final_b = resolved.state_for("B")

    assert final_a.board is not None
    assert final_b.board is not None
    assert final_a.board.active_id == "a-bench"
    assert final_b.board.active_id == "b-bench"
    assert final_a.ledger.exchangeable.count(
        "a-active-class",
        "discard",
    ) == 1
    assert final_b.ledger.exchangeable.count(
        "b-active-class",
        "discard",
    ) == 1
    assert_conserved(initial_a, final_a.ledger)
    assert_conserved(initial_b, final_b.ledger)

    assert mark_additional_knock_out(
        growing,
        player_id="unknown",
        pokemon_id="a-active",
    ) is None
    assert mark_additional_knock_out(
        growing,
        player_id="A",
        pokemon_id="missing",
    ) is None

    print("growable Knock Out context regressions passed")


if __name__ == "__main__":
    main()
