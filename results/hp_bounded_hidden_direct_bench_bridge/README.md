# Poffin's two-target public signal and K1 hidden-state bridge

## Question

Can an HP-constrained Buddy-Buddy Poffin direct-Bench search reveal two
public Pokémon print identities while preserving the actor's private Prize
knowledge, exact physical placement, and the subsequent shuffled top?

**Yes.** The [printed-HP-constrained Item adapter](../hp_bounded_direct_bench_transaction/)
now composes with the existing multi-target direct-Bench hidden-state bridge.

Implementation: `tools/hp_bounded_hidden_direct_bench_bridge.py`  
Regression: `results/hp_bounded_hidden_direct_bench_bridge/reproduce.py`  
[Green CI run 38240238284](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38240238284)

## Source and model

The Poffin profile is the legal `sv5-144` Item: search for up to two Basic
Pokémon with printed HP at most 70 and put them directly onto the Bench.

The wrapper requires the full candidate universe to pass trusted, exact
legal print and HP checks before invoking the existing Bayesian bridge.
It also derives the public signal from the **sorted multiset of physical
selected print IDs**. The caller cannot label an 80-HP or otherwise different
public Pokémon as though a legal low-HP target entered the Bench.

Selection order on the Bench does not change the public multiset label,
and duplicate print identities retain their multiplicities.

## Exact small-world witness

The hidden six-card pool has singleton Elgyem `sm11-90` (L, 60 HP),
Sprigatito `sv1-13` (S, 70 HP), Murkrow `me55-93` (H, 80 HP), and
three filler cards. Exactly two of the six occupy face-down Prize slots.
Poffin itself is already held in hand.

The actual world has **H and one filler Prized**, with both eligible Basics
and two fillers in the searchable deck.

The public policy searches both L and S when neither is Prized. Other Prize
compositions produce the different observation label `OTHER`. The visible
actual observation is `sm11-90|sv1-13`, generated from the exact selected
prints, not independently asserted.

There are 30 equiprobable ordered Prize pairs. Exactly 12 allow L and S
both to remain in the deck. Conditional on this public event, the opponent
knows both eligible Basics were unprized. Among the four remaining possible
Prize-source cards H and the three fillers, H is unprized in half of the
allowed worlds. When H is unprized, it makes up one of the two remaining
shuffled-deck cards.

Thus, with an actual uniformly sampled deck top:

| Observer | Probability next top is 80-HP Murkrow |
| --- | ---: |
| Searching player after full deck inspection (K1) | 0 |
| Other player observing both public Bench targets | 1/4 |

An independent combinatorial calculation gives the latter value:
`P(H unprized | both eligible targets) * P(top=H | H unprized) =
(1/2)*(1/2)=1/4`.

The physical transition also verifies that the observed Elgyem and
Sprigatito enter `in_play` with stable IDs, Poffin is discarded, no
target is placed in hand, staging is empty, and the sampled exact filler
top has positive support under both observer posteriors.

## Strategic meaning

A two-target search simultaneously changes the board and leaks information
about the remaining pool. K1 gives the searching player more exact Prize
information than the opponent obtains from the two face-up Bench cards.
A strategy that chooses which eligible pair to fetch according to Prized
cards can leak additional information through that policy.

These are distinct dimensions from the physical HP eligibility gate, so
the simulator should preserve the three together:
typed legal selection, observable target signaling, and player-relative
post-search beliefs.

## Limits

The six-card example is deliberately small and fully reproducible.
It does not estimate real match win rates, opening-hand success, opponent
play, Energy availability, evolving the new Basics, or future attacker
sequencing. The policy model in this result is stipulated and deterministic.
General strategies may use stochastic or matchup-dependent target policies.
The wrapper currently supports positive one- or two-target Item searches;
a zero-selection branch is intentionally excluded from the existing
multi-target bridge.
