# Canonical private-world sampling before native policy evaluation

**Status:** an experimental research-owned state-sampling seam and a pinned-engine physical-observation regression. It is deliberately separate from the authoritative live game and does not establish a correct competitive bot.

## Problem and purpose

The [verified native hidden-order oracle](../twinleaf_hidden_topdeck_oracle/) showed that `SimpleTacticsAi` uses actual unrevealed deck order when deciding whether to play search Items. The [narrow K0 Item tactic](../twinleaf_blind_topdeck_search/) repairs only Pokégear/Trainers' Mail decisions by a hypergeometric heuristic. A more general policy boundary must let all speculative tactics operate on a hypothetical state drawn independently of the *actual* hidden allocation.

The new [sampling module](../../../simulation/twinleaf/k0-hidden-world-sampler.cjs) constructs an independent Twinleaf `Simulator(state).store.state` clone. It uses only a deliberately defined visible projection to seed SHA-256-based deterministic sampling, sorts hidden cards canonically by print `fullName`, and reassigns sampled cards among private zones. For the actor, the private pool is own deck plus Prize cards; their hand remains unchanged. For the opponent, the private pool includes hand, deck and Prizes. Zone sizes remain unchanged. Each player's cards stay owned by that player.

The proposed sampler's target invariant is:

> If two game states have identical modeled public observations and equal hidden multisets for each player, the names and zone allocation of their sampled policy-world cards are identical even when the actual hidden worlds differ.

This is a **current-state** observational equivalence requirement within an explicitly restricted information model. It is not a perfect reconstruction of every fact a skilled player has seen earlier.

## Validation

The [standalone native-engine test](../../../simulation/twinleaf/test-k0-hidden-world-sampler.cjs) constructs four complete 60-card physical worlds using the pinned 2026-10-12 Twinleaf revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. It includes: Boss's Orders at different invisible deck depths; the same Boss's Orders held among initial face-down Prizes; and a change in the opponent's hidden hand-versus-deck allocation.

The SFT checks that the pre-sampling native Pokégear tactic changes play/hold based solely on the secret topdeck position; the public projections are equal; the authoritative original hidden arrays are untouched; the sampler preserves the declared public view, the actor's exact hand and physical zone sizes; all hypothetical hidden card-name arrays match across the four worlds; and native `PlayTrainerTactic` plus full `SimpleTacticsAi`, applied to the sampled states, give identical decisions across those paired worlds.

## Scope and validity boundaries

This sampler does not yet implement a complete paper Expanded belief state. In particular:

- It implicitly treats the **opponent's full remaining private-card multiset as known**. That is an open-decklist research assumption and can leak unseen deck construction in realistic closed-list play.
- It disregards card-history observations, including K1 known Prize composition, known deck positions, revealed opponent cards, previous shuffles, and targeted removal information. The modeled public projection is a policy boundary candidate, not an official full player observation API.
- A native tactic running on **one sampled world** can still value the sampled future outcome with hindsight. This hypothetical sample is independent of the *true* hidden order, yet one-sample planning is an uncalibrated decision heuristic. Expected-action evaluation over the full belief distribution is a separate requirement.
- One-step legality must still be checked against the original physical state and the actual game must never receive hypothetical card movement. Persistent policy RNG, rule-hook validation, and source-specific effects remain necessary.

A game replay or deck-ranking result obtained under this sampler should carry its own policy version and assumptions. It cannot be compared to native-bot outcomes as if the policies or information regimes were identical. The sampler is not currently activated by the main match runner; it exists for validation and future policy experiments.
