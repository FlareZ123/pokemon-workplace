"""Conserved Peonia setup for a known-position Greedy/Dream/Jirachi Prize line.

Four Prizes remain. Peonia exchanges three existing face-down cards for
Greedy Dice, Dream Ball and Jirachi Prism Star in controlled positions.
A supplied two-Prize Knock Out then opens the E-31 pending sequence.
"""

from __future__ import annotations

from fractions import Fraction

from board_position_state import BoardPokemon, PokemonCard
from e31_greedy_order_physical import play_dream, play_greedy, profiles_and_target
from identity_materialization import CardInstance, IdentityLedger, assert_conserved, move_instance
from multicopy_zone_state import ZoneCountState
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import stage_prize_takes
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState


def initial_physical():
    instances = [
        CardInstance("top", "TOP", "Top", "deck_top"),
        CardInstance("peonia", "swsh6-149", "Peonia", "hand"),
        CardInstance("greedy", "xy11-102", "Greedy Dice", "hand"),
        CardInstance("dream", "swsh7-146", "Dream Ball", "hand"),
        CardInstance("jirachi", "sm7-97", "Jirachi ◇", "hand"),
        CardInstance("chansey", "sv3pt5-113", "Chansey", "prize"),
        CardInstance("prize-one", "OLD-1", "Old Prize 1", "prize"),
        CardInstance("prize-two", "OLD-2", "Old Prize 2", "prize"),
        CardInstance("filler", "FILLER", "Filler", "prize"),
    ]
    pokemon = []
    for index in range(5):
        pkmn = "active" if index == 0 else f"bench-{index}"
        card_id = f"base-{index}"
        instances.append(CardInstance(
            card_id, f"BASE-{index}", f"Base {index}", "in_play",
            board_object_id=pkmn,
        ))
        pokemon.append(BoardPokemon(
            pkmn, (PokemonCard(card_id, f"Base {index}"),),
            retreat_cost=1,
        ))
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("sm2-60", "deck"): 1}),
        tuple(sorted(instances, key=lambda row: row.instance_id)),
    )
    board = PromotionPendingState(ledger, tuple(pokemon), active_id="active")
    prizes = TopPrizePhysicalState(
        ledger,
        "top",
        ("chansey", "prize-one", "prize-two", "filler"),
        (False, False, False, False),
    )
    return ledger, board, prizes


def play_peonia(board, prizes):
    """Choose three Prize slots, exchange exactly three hand cards face-down.

    All replacement positions are tracked. No shuffle occurs.
    """
    if board.ledger != prizes.ledger:
        raise ValueError("physical states disagree")
    original = prizes.ledger
    selected = ("chansey", "prize-one", "prize-two")
    replacements = ("greedy", "dream", "jirachi")
    if tuple(prizes.prize_instance_ids[:3]) != selected:
        raise ValueError("unexpected Peonia selection")
    if board.open_bench_slots != 1:
        raise ValueError("expected one open Bench slot")
    for instance_id in selected:
        if original.instance(instance_id).zone != "prize":
            raise ValueError("Peonia selected instance outside Prize zone")
    for instance_id in replacements:
        if original.instance(instance_id).zone != "hand":
            raise ValueError("Peonia replacement instance must be in hand")

    ledger = original
    for instance_id in selected:
        ledger = move_instance(ledger, instance_id, "hand")
    for instance_id in replacements:
        ledger = move_instance(ledger, instance_id, "prize")
    ledger = move_instance(ledger, "peonia", "discard")

    after = TopPrizePhysicalState(
        ledger, prizes.top_instance_id,
        ("greedy", "dream", "jirachi", "filler"),
        (False, False, False, False),
    )
    assert ledger.instance("chansey").zone == "hand"
    assert all(ledger.instance(i).zone == "prize" for i in replacements)
    assert_conserved(original, ledger)
    return board.with_ledger(ledger), after


def run_seeded(*, heads: bool):
    before, board, prizes = initial_physical()
    board, prizes = play_peonia(board, prizes)

    # A separately supplied one-hit knockout of a two-Prize opponent selects
    # exactly the two seeded Items. The Peonia Supporter was already spent.
    staged = stage_prize_takes(prizes, positions=(0, 1))
    board = board.with_ledger(staged.physical.ledger)
    order = PendingPrizeBatchOrder.from_staged(staged)
    greedy, dream, target, action = profiles_and_target()

    pending = order.choose_next("greedy")
    pending, board = play_greedy(
        pending, board, greedy,
        heads=heads, extra_position=0,
        use_jirachi=True,
    )
    order = order.advance_after_resolution(
        pending, resolved_instance_id="greedy",
    )
    assert order is not None

    # Greedy's nested Prize chain finishes before resolving Dream Ball.
    pending = order.choose_next("dream")
    pending, board = play_dream(
        pending, board, dream, target, action,
    )
    assert order.advance_after_resolution(
        pending, resolved_instance_id="dream",
    ) is None

    assert pending.pending == ()
    assert pending.physical.ledger == board.ledger
    assert_conserved(before, board.ledger)
    assert board.ledger.instance("peonia").zone == "discard"
    assert board.ledger.instance("chansey").zone == "hand"
    assert all(row.pokemon_id != "chansey" for row in board.pokemon)
    assert board.open_bench_slots == 0

    newcomers = {row.pokemon_id for row in board.pokemon}
    remaining = len(pending.physical.prize_instance_ids)
    if heads:
        assert "bonus-jirachi" in newcomers
        assert "dream-target" not in newcomers
        assert remaining == 0
        assert board.ledger.instance("filler").zone == "hand"
        return 4, "Jirachi ◇"
    assert "dream-target" in newcomers
    assert "bonus-jirachi" not in newcomers
    assert remaining == 2
    assert board.ledger.instance("jirachi").zone == "prize"
    return 2, "Tapu Lele-GX"


def main() -> None:
    tail = run_seeded(heads=False)
    head = run_seeded(heads=True)
    assert tail == (2, "Tapu Lele-GX")
    assert head == (4, "Jirachi ◇")
    expected = (Fraction(tail[0]) + Fraction(head[0])) / 2
    assert expected == 3
    print("Peonia-seeded E-31 position control: both physical coin branches passed")
    print(f"coin tails: {tail}; coin heads: {head}; expected prizes: {expected}")


if __name__ == "__main__":
    main()
