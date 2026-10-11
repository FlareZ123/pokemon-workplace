# Exact optional-Lunar-Cycle quotient of physical Bench-contraction histories

## Research question

Given the five-Bench evolved-Spidops fixture, how many distinct conserved full game states remain from `5 -> 4 -> 3` when the player may use Lunatone's Lunar Cycle between contractions?

With no intervening action there are **20** discard-order histories and **10** distinct complete physical terminal states. With an optional Lunar Cycle at the intermediate state, there are **32** action-annotated histories and **19** distinct full terminal states.

Implementation: `tools/bench_contraction_action_equivalence.py`.  
[GitHub Actions run 38132538881 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132538881).

## Physical source state

The fixture comes from `bench_contraction_intermediate_action.print_specific_fixture()`.

- Five Benched Pokémon, one Active Bidoof.
- `me1-74` Lunatone with **Lunar Cycle**, whose printed Ability requires Solrock in play and a Basic Fighting Energy discarded from hand to draw three.
- `pgo-39` Solrock as the required other Pokémon.
- An evolved Tarountula → Spidops carrying materialized Grass Energy and Muscle Band.
- Regirock and Regice as remaining Bench occupants.
- One Basic Fighting Energy in hand and three explicitly modeled draw cards in deck.

The model treats capacity changes as already-authorized physical events and one Lunar Cycle resolution as legal if its required Pokémon and payment remain available. It does not implement a full turn scheduler or lock status.

## Exhaustive procedure

1. Enumerate all five possible chosen first discards to capacity four.
2. For each result, enumerate all four possible second discards to capacity three.
3. At the intermediate state, use the printed Ability if possible, optionally also considering a skip branch.
4. For each branch, apply the second chosen contraction through the existing physical conservation engine.
5. Compare final `StackBoardMaterialState` objects and aggregate truly equal states. Validate all card-class totals.

The 20 initial choice histories split into:

| Intermediate/final ability condition | Pure histories |
| --- | ---: |
| Ability available in both stages | 6 |
| Ability available only in intermediate stage | 6 |
| Ability unavailable in intermediate and final stages | 8 |
| **Total** | **20** |

Twelve histories permit an optional use, adding twelve action branches. That creates 32 annotated histories.

Among the ten possible final Bench survivor sets, nine have at least one history with Lunar Cycle available at the intermediate stage. Each of those nine gains a second distinct off-board resource state. One final survivor set can never arise from an intermediate Bench containing both required Pokémon, so it has only the baseline state.

Thus `10 + 9 = 19` distinct complete terminal states.

All terminal states preserve full materialized Pokémon stacks and attachments, preserve card-class counts, and retain correct discard routing. Equal survivor names alone would incorrectly merge nine pairs of different resource states.

## Stronger validation

The check also verifies a local action-commutation property. For the six histories where the ability remains available after direct contraction, applying the effect before the second contraction produces exactly the same full state as applying it after direct contraction. In the six histories where a required Pokémon is lost during the second contraction, the action is only possible in the intermediate state and changes the final ledger.

This supports the distinction between action placement that *commutes* with contraction and action placement whose enabling source disappears.

## Limits

The deterministic three-card draw is a controlled exchangeable-count transition, not a randomized deck or complete card text interpreter. Use of Lunar Cycle is constrained to one available activation; other Ability locks, timing quotas, tools, Stadiums, opponent turns, and detailed win probability are outside this experiment.

The general formula, independent of this particular five-object physical witness, appears in [bench_intermediate_guard_equivalence](../bench_intermediate_guard_equivalence/).
