# The nonanticipativity gap in discard decisions

## Question

An attack's discard can preserve exactly one of three Basic Energy cards alongside Double Dragon Energy. If the future attack's cost is **unknown when the discard is chosen**, can an optimizer count every cost for which *some* retaining choice would work?

**No.** That counts a clairvoyant policy able to condition its past discard on information received afterward. A policy must choose which two Basics to discard **at the time of payment**.

This is a controlled information-timing theorem for resource planners. It does not assert that Regidrago VSTAR's known Grass/Grass/Fire attack cost is hidden; Regidrago itself serves only as the source of the two-unit DDE-and-Basic payment structure.

## Resource model

One active Double Dragon Energy (`xy6-97`) and three single-unit Basic Energy cards are attached to a Dragon Pokémon. A current attack requires discarding two generic Energy units. Discarding two Basics retains DDE plus one Basic of the player's choice. The next attack has a three-symbol cost selected from the nine Basic Energy types and Colorless.

Consider three policies:

- **Discard DDE:** retain all three Basics, with their limited specific colored provision.
- **Fixed choice:** before the future cost becomes known, choose which Basic to retain alongside DDE. Afterward, readiness is evaluated against the revealed cost.
- **Clairvoyant choice:** first reveal the future cost, then choose whichever Basic best matches it, while retaining DDE.

Only the first two are information-admissible when the future cost is unknown at the time of the attack's discard.

## Exact result under a deliberately uniform cost-signature prior

There are 220 unordered three-symbol future attack-cost signatures using nine colors plus Colorless. All signatures receive equal artificial weight.

| Distinct Basic types among the three attached cards | Basic-type mixtures in scope | Coverage after discarding DDE | Coverage retaining DDE with one Basic chosen in advance | Clairvoyant coverage choosing Basic after seeing future cost | False availability from clairvoyance |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9 | 4 | 100 | 100 | 0 |
| 2 | 72 | 6 | 100 | 136 | 36 |
| 3 | 84 | 8 | 100 | 164 | **64** |

With three distinct Basic Energy types, treating a discard policy as if it knows the later attack cost counts **164** reachable signatures. Every genuine fixed discard choice reaches only **100**. The difference, **64/220 = 29.0909 percentage points**, is the overstatement produced by an ex-post existential choice under a uniform 220-signature objective.

With two distinct types the analogous gap is **36/220 = 16.3636 percentage points**. With three identical Basics there is no information advantage because all retaining decisions leave the same Basic type.

## Derivation

For DDE plus one retained Basic of type X, the future three-cost is feasible if it includes X or at least one Colorless symbol. DDE covers the other two symbols. The excluded costs are colored-only three-multisets from the eight types other than X, giving

`220 - C(10,3) = 100`

cost signatures, independent of X.

If there are `k` distinct Basic types among the three, a clairvoyant discard can select one matching any of those types. The excluded costs consist of three colored symbols drawn from the remaining `9-k` colors, giving

`220 - C(11-k,3)`.

For `k=1,2,3`, this yields `100, 136, 164`.

Discarding DDE leaves three Basics. Exactly four, six, or eight cost-signature multisets can be covered, depending on whether the three Basics have one, two, or three distinct types: each covered signature is obtained by replacing some of their provided colored symbols with Colorless cost symbols.

The rules of Colorless matching matter: any supplied Energy unit can fill a Colorless *attack cost*, whereas a typed Energy discard instruction still requires exact provider types.

## Why this matters to a deck optimizer

A graph can appear well connected because the optimizer asks whether some payment preserves each of many different future attacks. If the identity of the attack need is learned **after** the discard, those individually feasible routes need not coexist in a single actionable policy.

With a nonuniform belief `p(c)` over possible future cost signatures, the actual best advance choice is

`max_x sum_c p(c) * 1[ready(DDE + Basic x, c)]`

while the clairvoyant optimistic upper bound is

`sum_c p(c) * max_x 1[ready(DDE + Basic x, c)]`.

The first quantity selects one Basic for all future uncertainty states. The second changes its earlier discard across futures and may substantially overvalue the option.

This illustrates **nonanticipativity** in sequential planning, a stricter abstraction than simple reachability or post-hoc graph connectivity. The same issue can arise in one-use Trainer searches, Supporter contention, hidden Prize information and Bench-slot commitments.

## Verification

`tools/energy_discard_nonanticipative_coverage.py` enumerates all 165 Basic-type mixtures and 220 cost signatures, checks the source Double Dragon Energy print text, computes fixed and clairvoyant coverage using the repository's attack-cost-aware matcher, and asserts the exact combinatorial closed forms for every mixture.

Run `python -m tools.energy_discard_nonanticipative_coverage` at the repository root.

## Limitations

The model uses a **uniform prior over abstract cost signatures**, not a measured distribution of real cards, matches or decks. The future three-symbol cost is an exogenous hidden target in this thought experiment; in many Pokémon TCG states the relevant attack's cost is already public and known. It omits opponent actions, resource recovery, Energy attachment timing, attack effects and win conditions.

The result sharpens the distinction between a feasible line conditional on future knowledge and a physically implementable strategy.
