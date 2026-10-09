# Physical Bench contraction as a choice space, not a single predetermined successor

## Research question

How should a physical-state game simulator represent a forced Bench contraction when the affected player may choose which Pokémon to discard?

Enumerate every legal survivor set first, then let the strategic policy choose a successor. Collapsing the transition to a single additive-value ranking can irreversibly discard an engine component that has very little individual value but large value in combination.

This work supplies `tools/bench_contraction_choice_space.py`, a pure adapter over the existing `board_object_kernel.BoardState`.

## Rules grounding

The Advanced Player's Rulebook identifies five normal Bench slots and only one Active Pokémon. Current paper Expanded card text for Collapsed Stadium and Parallel City tells the affected player to discard excess Benched Pokémon until the allowed size is reached.

The choice of **which specific Benched Pokémon** to discard is a legal decision point. It requires preserving each distinct possible survivor set until the strategy selects one.

This model covers the immediate geometric step after the capacity restriction has been determined. It returns removed full `BoardPokemon` objects but does not move their constituent physical cards into an explicit discard-zone ledger; that belongs to the downstream zone/conservation layer. Forced Bench discard is not a Knock Out.

## Enumerating successors

Given a valid board `B`, `n` Benched Pokémon and a new capacity `C`, retain exactly `k=min(n,C)` Bench objects. Every size-`k` combination produces a physically distinct legal survivor set under this simple contraction rule.

The number of possible states is `binomial(n,k)`.

Examples:

| Original occupancy | New capacity | Legal survivor sets |
| ---: | ---: | ---: |
| 5 | 4 | 5 |
| 5 | 3 | 10 |
| 8 | 5 | 56 |
| 8 | 4 | 70 |

These counts are small enough for exhaustive branching. This is especially important because all currently cataloged expanded-capacity effects in the provided card snapshot allow at most eight Benched Pokémon.

Each successor preserves the Active Pokémon and all surviving Bench objects, including their attachments, damage, and identity. Removed objects are returned separately, retaining their identities for later zone-conservation steps.

## Physical witness: joint survival differs from additive cleanup

Five Benched objects are assigned illustrative continuation values:

- `E`, primary attacker: 100;
- `A`, Lunatone `me1-74`: 0;
- `B`, Solrock `pgo-39`: 0;
- `C`, attacker: 22;
- `D`, alternative attacker: 20.

The Active object is a separate Bidoof and occupies no Bench slot.

A pairwise model awards an illustrative +30 when `A` and `B` survive together, motivated by Lunatone's Lunar Cycle requiring Solrock in play.

The existing convenience function `board_object_kernel.contract_bench()` resolves this state using independent occupant `retention_value` fields and discards `A` or `B`. This is consistent with its **intended additive-value heuristic**, but it removes the Lunar Cycle pair relationship.

The new choice enumerator produces five physically legal successor states for the 5-to-4 contraction. A downstream joint-value selector instead discards `D`, retaining `E,A,B,C` with illustrative utility **152**. This is a different strategic decision produced from the *same legal starting board*.

From that survivor set, a later 4-to-3 contraction can keep `E,A,B` with utility **130**. Starting directly at the original five and contracting to three could instead retain `E,C,D` worth **142**. This physically instantiates the irreversible-future-choice counterexample documented in [bench_synergy_contraction/](../bench_synergy_contraction/).

## Tests

Run `python tools/bench_contraction_choice_space.py --self-test` for five regressions:

1. 5-to-4 and 5-to-3 successor counts;
2. contrast with the additive default transition;
3. physically consistent sequential contraction and nonnested optimal survivor sets;
4. exact counts and object-ID conservation across capacities 0 through 8;
5. explicit full-Pokémon return for a discarded object without treating it as a Knock Out.

Run without flags to print a compact JSON summary of the additive and joint-utility first-stage choices.

The [GitHub Actions regression passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919888218).

## Integration design

**Mechanics** should enumerate or apply an explicitly chosen discard set. **Strategy** should rank the legal successors using a state-relative continuation evaluator, potentially with card dependencies, locks, information timing, and future opponent actions.

The current `contract_bench()` additive heuristic can remain useful for specific models and as a deterministic baseline. The new `contraction_choices()` function supplies the full branching semantics for models whose objective requires a different choice.

## Limits and next steps

This is an immediate physical-geometry projection rather than a whole turn engine. It does not model the exact time a Stadium enters/leaves play, the priority/order of multiple contracting effects, special card-text exceptions, abilities triggered by a departure, loss of attachments into the discard pile, or shared conservation over the hand/deck/Prize zones. It assumes the affected player chooses among the excess Bench objects.

Next, integrate selected discard branches into the repository's physical zone-exit ledger while keeping the strategic selection explicit. Compare a reactive immediate-utility selector against a continuation-aware decision policy when a further contraction or opposing gust is possible.
