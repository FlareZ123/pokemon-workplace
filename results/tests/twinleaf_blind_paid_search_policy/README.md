# Observation-consistent K0 paid-search diagnostic policy

**Status:** three exact implemented Item prints; pinned Twinleaf
`3348ebdc898f175a2ed8f999133cd13d1afd01f5`; NOT an independently
validated competitive bot. This result is about information integrity.

## Problem addressed

[The hidden-Prize oracle](../twinleaf_hidden_prize_search_oracle/)
demonstrates that native `PlayTrainerTactic` uses actual undisclosed
deck-versus-Prize placement to decide whether to spend Quick Ball,
Ultra Ball or Mysterious Treasure. A player who has not yet searched
their deck (K0) cannot condition on that secret placement.

## Exact scope and executable mechanism

[The research tactic](../../../simulation/twinleaf/blind-paid-search-tactic.cjs)
subclasses pinned native `PlayTrainerTactic` and changes the pre-play
decision for exactly:

| Card implementation | Discard cost | Search targets |
| --- | ---: | --- |
| Quick Ball SSH | One other hand card | Basic Pokémon |
| Ultra Ball SVI | Two other hand cards | Any Pokémon |
| Mysterious Treasure FLI | One other hand card | Psychic or Dragon Pokémon |

For each eligible Item, it computes the K0 exchangeable-pool
probability of at least one eligible card being inside the remaining
deck. The hidden pool comprises all *own* cards in the deck together
with all own face-down Prize cards, which is inferable from the
complete known decklist and public removals when K0's exchangeability
assumption holds.

With total unseen pool size `N`, `h` eligible hidden cards, and
`d` deck positions, the calculation is:

`P(searchable target) = 1 - C(N-h, d) / C(N, d)`.

The same calculation for Basic-eligible targets estimates the
incremental opportunity to establish a Basic from an empty Bench.
The scoring surrogate weights those probabilities by the pinned
native hand-score coefficients, subtracts the printed Item's hand
value and applies marginal discard-payment losses from the pinned
`StateScore.getCardScore` routine. Only **visible hand state** affects
which card is a possible payment. A positive estimated delta chooses
the Item; native `SimpleTacticsAi` still validates the actual action.

The tactic does not peek at the *partition* of unknown cards between
the real deck and face-down Prizes, and it does not inspect their
secret deck order. Unlike a sampled hypothetical deck, it integrates
the target-availability event exactly under the stated K0 prior.

## Verification

[Quick Ball SFT](../../../simulation/twinleaf/test-hidden-prize-search-oracle.cjs)
and [Ultra Ball/Mysterious Treasure SFT](../../../simulation/twinleaf/test-hidden-prize-extended-search-oracle.cjs)
compare the native tactic and the new one across 156 complete
60-card-conserving hidden worlds. For each of the three Items:

- Native policy: play in all 46 worlds with the only eligible Basic
  in deck, hold in all six worlds where it is Prized.
- K0 policy: make the **same play decision in all 52 worlds**.
- Both variants are exercised through real
  `SimpleTacticsAi.decodeNextAction`, including native action validity.
- Additional zero-target and insufficient-payment states confirm
  public target and payment gating.

[Green 156-world CI 38610529023](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38610529023).

The runner retains `native`, `blind_topdeck`, `sampled_k0`
and a separately labeled `blind_paid_search` policy mode.
The report explicitly identifies
`three_paid_search_prints_k0_blind_other_native_tactics_unmasked`,
with hook `k0_blind_paid_search_three_prints_v1`, rather than
misrepresenting the policy as globally fixed.

## Live bounded implementation smoke test

[Green paired-match CI 38611295606](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38611295606)
ran a single seed pair, `20261014`, across both seats for the published
Aichi Shadow Rider versus Regidrago source decks at research revision
`cccf6c4d3d3a06341a1f850ba9d7fb2ac3072884`.

- Orientation A Shadow Rider / B Regidrago: completed in 243 actions
  and 14 attacks; Shadow Rider won under the engine.
- Orientation A Regidrago / B Shadow Rider: completed in 226 actions
  and 12 attacks; Regidrago won under the engine.
- Both games finished without engine/policy errors, censored outcomes
  or unresolvable terminal values. First seat won both games.
- The two games are **one paired diagnostic sample**, not two
  independent matchup observations. They cannot estimate a real
  paper Expanded win rate.

That workflow also found a stale Hook roster test that failed after a
new Mega Absol Terminal Period correction had been added. Agent 26
repaired the two expected-roster assertions and included the already
existing Mega Absol SFT in paired CI. The subsequent smoke run passed.

## Limitations and immediate priority

This estimator is a first-order hand-score heuristic. It does not
solve discard DCI/UDP, card synergy, target contention or Bench
opportunity costs beyond one narrow Basic setup bonus. The combined
unseen-pool prior is strictly a K0 assumption and may be wrong after
the player has searched their deck (K1), manipulated or learned exact
Prize locations, or tracked order. Its native fallback for every
other Item remains a potential hidden-information oracle. Native
Supporters, opposing secret hands, evolution and attack policies
also remain unaudited.

A stronger observation-consistent full-game decision process is
needed before using self-play to compare competitive deck strength.
Preserve policy source revision, modeled observation regime,
probability assumptions and exact search print support in every
experiment. Continue adversarial invariance testing and build a K1
information-tracker before lifting these bounds.
