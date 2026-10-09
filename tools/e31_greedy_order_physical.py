"""Physical Prize/Bench trace for Greedy Dice, Dream Ball and nested Jirachi.

Crosschecks every branch of the small exact strategic model against the
repository's materialized-card, E-31, typed-search, and Bench kernels.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

from before_hand_prize_executor import (
    begin_before_hand_item_play,
    finish_before_hand_item_play,
    resolve_before_hand_item_effect,
)
from before_hand_prize_profiles import build_before_hand_prize_profiles
from board_position_state import BoardPokemon, PokemonCard
from dream_ball_typed_bench_execution import (
    dream_ball_target_from_metadata,
    execute_dream_ball_item_transaction,
)
from e31_greedy_order_option import (
    DREAM, FILLER, GREEDY, JIRACHI, TARGET, resolve as abstract_resolve,
)
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from prize_before_hand_bench_entry import use_wish_upon_a_star
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import (
    resolve_next_pending_prize,
    stage_additional_prize_front,
    stage_prize_takes,
)
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand

ROOT = Path(__file__).resolve().parents[1]


def make_state(jirachi_first: bool):
    instances = [
        CardInstance("top", "TOP", "Top", "deck_top"),
        CardInstance("greedy", "xy11-102", GREEDY, "prize"),
        CardInstance("dream", "swsh7-146", DREAM, "prize"),
    ]
    last = (
        (("jirachi", "sm7-97", JIRACHI), ("filler", "FILLER", FILLER))
        if jirachi_first else
        (("filler", "FILLER", FILLER), ("jirachi", "sm7-97", JIRACHI))
    )
    for instance_id, card_class, name in last:
        instances.append(CardInstance(instance_id, card_class, name, "prize"))

    pokemon = []
    for index in range(5):
        pokemon_id = "active" if index == 0 else f"bench-{index}"
        instance_id = f"base-{index}"
        instances.append(CardInstance(
            instance_id, f"BASE-{index}", f"Base {index}", "in_play",
            board_object_id=pokemon_id,
        ))
        pokemon.append(BoardPokemon(
            pokemon_id, (PokemonCard(instance_id, f"Base {index}"),),
            retreat_cost=1,
        ))

    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("sm2-60", "deck"): 1}),
        tuple(sorted(instances, key=lambda card: card.instance_id)),
    )
    board = PromotionPendingState(ledger, tuple(pokemon), active_id="active")
    physical = TopPrizePhysicalState(
        ledger, "top",
        ("greedy", "dream", *(card[0] for card in last)),
        (False, False, False, False),
    )
    prizes = stage_prize_takes(physical, positions=(0, 1))
    assert board.open_bench_slots == 1
    return ledger, prizes, board.with_ledger(prizes.physical.ledger)


def profiles_and_target():
    profiles = {
        profile.card_id: profile
        for profile in build_before_hand_prize_profiles(ROOT / "resources")
    }
    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    target = dream_ball_target_from_metadata(metadata["sm2-60"], copies=1)
    allocated = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        (target.search_target.group,),
        (make_demand("pokemon", "Pokemon"),),
    )
    action = next(
        a for a in allocated.actions
        if a.output == (1,) and a.target_cost == (1,)
    )
    return profiles["xy11-102"], profiles["swsh7-146"], target, action


def play_dream(prizes, board, dream_profile, target, action):
    if board.open_bench_slots == 0:
        after = resolve_next_pending_prize(prizes).after
        return after, board.with_ledger(after.physical.ledger)

    transaction = execute_dream_ball_item_transaction(
        prizes, board,
        profile=dream_profile,
        during_own_turn=True,
        targets=(target,),
        search_action=action,
        pokemon_id="dream-target",
        instance_id="dream-card",
    )
    return transaction.after_prizes, transaction.after_board


def play_greedy(prizes, board, greedy_profile, *, heads, extra_position,
                use_jirachi):
    resolving = begin_before_hand_item_play(
        prizes, greedy_profile, during_own_turn=True,
    )
    effect = resolve_before_hand_item_effect(resolving, coin_heads=heads)
    current = resolving.pending_state()
    board = board.with_ledger(current.physical.ledger)

    if effect.additional_prize_awards:
        current = stage_additional_prize_front(current, position=extra_position)
        board = board.with_ledger(current.physical.ledger)
        extra = current.pending[0].instance_id

        if extra == "jirachi" and use_jirachi:
            wish = use_wish_upon_a_star(
                current, board,
                pokemon_id="bonus-jirachi",
                during_your_turn=True,
                extra_prize_position=0,
            )
        else:
            wish = None

        if wish is None:
            current = resolve_next_pending_prize(current).after
            board = board.with_ledger(current.physical.ledger)
        else:
            current = wish.after_prizes
            board = wish.after_board
            assert wish.extra_prize_staged
            # Wish Upon a Star staged the last inert Prize as nested work.
            assert current.pending[0].instance_id == "filler"
            current = resolve_next_pending_prize(current).after
            board = board.with_ledger(current.physical.ledger)

    after = finish_before_hand_item_play(
        effect,
        continuation_state=current,
        additional_prizes_resolved=bool(effect.additional_prize_awards),
    )
    return after, board.with_ledger(after.physical.ledger)


def run_physical(*, order, jirachi_first, heads, selected_position,
                 use_jirachi, deps):
    initial, prizes, board = make_state(jirachi_first)
    greedy_profile, dream_profile, target, action = deps
    order_context = PendingPrizeBatchOrder.from_staged(prizes)
    for card in order:
        prizes = order_context.choose_next("greedy" if card == GREEDY else "dream")
        if card == GREEDY:
            prizes, board = play_greedy(
                prizes, board, greedy_profile,
                heads=heads, extra_position=selected_position,
                use_jirachi=use_jirachi,
            )
            resolved = "greedy"
        else:
            prizes, board = play_dream(
                prizes, board, dream_profile, target, action,
            )
            resolved = "dream"
        order_context = order_context.advance_after_resolution(
            prizes, resolved_instance_id=resolved,
        )
    assert order_context is None
    assert not prizes.pending
    assert prizes.physical.ledger == board.ledger
    assert_conserved(initial, board.ledger)
    newcomer = (
        JIRACHI if any(row.pokemon_id == "bonus-jirachi" for row in board.pokemon)
        else TARGET
    )
    return 4 - len(prizes.physical.prize_instance_ids), newcomer


def main() -> None:
    deps = profiles_and_target()
    tested = 0
    totals: dict[tuple[bool, tuple[str, str]], dict[tuple[int, str], Fraction]]
    totals = defaultdict(lambda: defaultdict(Fraction))

    for known, order, jirachi_pos, heads, use_jirachi in product(
        (False, True),
        ((GREEDY, DREAM), (DREAM, GREEDY)),
        (0, 1),
        (False, True),
        (False, True),
    ):
        selected = jirachi_pos if known else 0
        actual = run_physical(
            order=order,
            jirachi_first=(jirachi_pos == 0),
            heads=heads,
            selected_position=selected,
            use_jirachi=use_jirachi,
            deps=deps,
        )
        abstract = abstract_resolve(
            order=order,
            remaining_prizes=(
                (JIRACHI, FILLER) if jirachi_pos == 0 else (FILLER, JIRACHI)
            ),
            greedy_heads=heads,
            selected_prize_position=selected,
            use_jirachi=use_jirachi,
        )
        expected = abstract.prize_count, abstract.bench_newcomer
        assert actual == expected, (known, order, jirachi_pos, heads,
                                    use_jirachi, actual, expected)
        if use_jirachi:
            totals[(known, order)][actual] += Fraction(1, 4)
        tested += 1

    assert totals[(False, (GREEDY, DREAM))][(4, JIRACHI)] == Fraction(1, 4)
    assert totals[(True, (GREEDY, DREAM))][(4, JIRACHI)] == Fraction(1, 2)
    assert all(
        (4, JIRACHI) not in totals[(known, (DREAM, GREEDY))]
        for known in (False, True)
    )
    print(f"Physical E-31 Greedy/Dream/Jirachi integration passed: {tested} branches")
    for (known, order), distribution in totals.items():
        print(("position-known" if known else "composition-only"), order,
              dict(distribution))


if __name__ == "__main__":
    main()
