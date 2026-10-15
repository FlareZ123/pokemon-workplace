# Shadow Rider vs. Iron Thorns: launch access and sustained Ability suppression

## Why the prior endpoint needs a continuation audit

The Aichi 2026 champion Shadow Rider Calyrex VMAX deck has a conditional anti-Path / Iron Thorns opening counterline studied in [the paid-search allocation analysis](../shadow_rider_paid_search_allocation/). Its model adds one hypothetical Canceling Cologne (`swsh10-136`) and one hypothetical Flutter Mane with Midnight Fluttering (`sv5-78`) while substituting other original 60-card slots. The model finds **7.327398814%** early launch access conditional on a Basic-valid opening seven, six hidden Prizes, one going-second natural draw, and a stipulated Path to the Peak + Active Iron Thorns ex board. This is a **K1-style information-privileged upper bound**, not a realizable K0 policy or match win rate.

A crucial continuation gate was previously implicit:

1. Canceling Cologne makes the opponent's Active Pokémon have no Abilities **until the end of the current turn**.
2. Radiant Eternatus's Climactic Gate puts up to two VMAX directly on the Bench and **ends the player's turn**.
3. Once Cologne expires, if Iron Thorns ex remains Active and has no other applicable suppression, Initialization switches back on and removes the Rule-Box VMAX's Underworld Door Ability. The two freshly placed VMAX have no attached Energy at launch.
4. The ordinary next-turn manual attachment alone cannot power a fresh VMAX's three-Colorless Max Geist, or even its two-Colorless Dimension Valley cost. Conditional acceleration such as Raihan after an opponent-turn KO is a separate possible exception.
5. An Active Flutter Mane's non-Rule-Box Midnight Fluttering can persist across the turn boundary if Flutter remains Active and survives. It can keep Initialization off while Underworld Door charges a Benched VMAX. When Flutter subsequently pivots away, the lock may reactivate, but that does not remove Energy already attached or prevent the ready VMAX from attacking.

The result below partitions **access to the early launch**, and describes which access states potentially preserve Underworld Door on the next turn. It does **not** calculate actual survival, charging, attack, damage, or wins.

## Exact K1-access partition

The [reproducer](reproduce.py) reuses the exact 60-card group counts, Prize-mask calculation and physical paid-source solver from the published paid-search model. It disables each counter channel in turn while retaining its starting-Basic geometry and the other channel's search contention. Specifically:

- The *Cologne-feasible* counterfactual keeps Flutter in the opening Basic count for board geometry, but removes Flutter's suppression role.
- The *Flutter-feasible* counterfactual removes held Cologne and Stone-to-Cologne selection while retaining the initial Active Flutter source and other search routes.
- Each state is categorized by exact union, intersection and exclusive channel identities. A source may be feasible even when the alternative source is also feasible.

| Route classification | Exact conditional probability |
| --- | ---: |
| Any feasible launch, established baseline | **7.327398814%** |
| Cologne-feasible (including overlap) | 4.127639078% |
| Flutter-feasible (including overlap) | 3.617383668% |
| Both routes feasible | 0.417623931% |
| **Cologne only** | **3.710015146%** |
| **Flutter only** | **3.199759737%** |

The categories satisfy `any = Cologne only + Flutter only + both`. Among launch-access successes, **50.632089782% are Cologne-only** and **49.367910218% have a Flutter-supported alternative**. A Flutter-supported opening still requires Flutter to survive the opponent's next turn, remain Active while charging the VMAX, have sufficient available Psychic Energy, and execute a legal pivot. These percentages are unconditional with respect to the *specific restricted conditional opening sample* and conditional only on its stated starting requirements.

## Validation

- Full 60-card exact weighted enumeration partitions every applicable initial hand, first draw and six-Prize exhaustion mask; it exactly reproduces the preceding study's 7.327398814% total.
- A separate exhaustive physical-card oracle enumerates **83,720** Basic-valid miniature worlds with individual labeled cards, three-card openers, one Prize and one natural draw. The oracle counts **2,490** successful launches, of which **528** are Cologne-feasible, **2,058** Flutter-feasible and **96** are feasible via both channels. The weighted small-world evaluator agrees exactly.
- Source-print assertions check `sv6-77` Initialization, `swsh10-136` Cologne duration, `swsh12pt5-105` Climactic Gate's turn termination, `sv5-78` Midnight Fluttering, `swsh6-75` Underworld Door/Max Geist, `xy4-93` Dimension Valley and `swsh7-152` Raihan.
- A minimal timed state regression checks Cologne expiry, Flutter persistence/KO, the availability of Underworld Door before versus after Flutter leaves Active, and an exceptional two-Energy Raihan-plus-manual upper bound. This is a **rules implication and state-bound test**, not a simulation of all possible gameplay.

Reproduce on Windows 11 or CI using `python -m results.tests.shadow_rider_thorns_continuation.reproduce`. The [manual-only validation workflow](../../../.github/workflows/validate-shadow-rider-thorns-continuation.yml) deliberately avoids automatic expensive runs.

## What this changes, and what it does not

The approximately 7.33% restricted initial launch-access endpoint combines two strategically different source routes. A launch that spends its only temporary Cologne has an immediate next-turn Underworld Door obstruction if Thorns stays Active; a Flutter-backed launch can potentially keep a charging window open. That difference could strongly affect which hypothetical tech card deserves a deck slot, but it would be premature to infer a matchup preference without measuring Flutter survival, second-turn hand Energy, turn-specific pivots, emergency KO-triggered Raihan, and lost tournament-source slots.

The original published champion 60 contains neither Cologne nor Flutter Mane. This counterfactual is experimental and does not alter the tournament result or claim an improved deck. The broader solver also remains K1 information-privileged, models only Psychic Energy as paid-search discard fodder, and omits competing strategic use of Items, Supporters, other lock counters and opponent game decisions.

**Next research:** joint simulation of launch route, opponent's first Volt Cyclone/other response, surviving Active Flutter, playable pivot, Underworld Door draw stream, next-turn Max Geist damage threshold, and opponent Prize race. Preserve exactly which source is used rather than inferring the next turn from a scalar launch probability.
