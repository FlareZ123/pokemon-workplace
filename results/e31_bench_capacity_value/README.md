# Exactly one free Bench slot creates a Greedy Dice / Dream Ball sequencing kink

## Question

Does the relative value of resolving Greedy Dice before Dream Ball, rather than after Dream Ball, rise smoothly with available Bench space?

In the controlled four-Prize E-31 case, **the order-sensitive bonus peaks at exactly one available Bench slot**. With no available slot, neither Dream Ball nor Jirachi can enter play. With two available slots, both can enter, so the original two sibling effects no longer compete for Bench space.

This is a discrete, non-monotone capacity effect and a direct test of state-dependent Active Move Realism (AMR).

Executable: [tools/e31_bench_capacity_value.py](../../tools/e31_bench_capacity_value.py).  
CI: [passing run 37977833525](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37977833525).

## Conditional four-Prize geometry

The same E-31 packet as [the original Greedy-order option study](../e31_greedy_order_option/) is used:

- Four Prizes remain just before a two-Prize Knock Out.
- The two selected face-down Prize cards are Greedy Dice and Dream Ball.
- The two other Prizes are Jirachi Prism Star and inert filler, both face down.
- Greedy Dice flips one fair coin. On heads it selects one remaining Prize slot.
- Dream Ball can bench an eligible Pokémon from deck when space permits.
- Jirachi can enter the Bench after being awarded from face-down Prizes and take one additional Prize when space permits.
- The attacking player is in their own turn and no lock or opposing effect intervenes.

Two position-information cases are enumerated:

1. **Composition-only:** both remaining Prize identities are known, but the Jirachi position is exchangeable. Greedy Dice's heads branch has probability `1/2` of selecting Jirachi.
2. **Private position-known:** Jirachi's exact remaining slot is known. On Greedy Dice heads, it can be selected with certainty.

A known-position setup can be supplied by Peonia's chosen face-down placement (see [the conserved Peonia witness](../e31_peonia_seed_execution/)). Ordinary K1 deck-search composition knowledge corresponds to the first case.

## Physical exact result

Let `q` be the probability that a heads Greedy Dice resolves into Jirachi:

- `q=1/4` with composition-only information: heads `1/2` times Jirachi hit `1/2`.
- `q=1/2` with position-known information: heads `1/2` times Jirachi hit `1`.

Every table entry is the exact expectation from four equally weighted physical worlds (two Prize layouts and two coin faces):

| Free Bench slots | Order | Expected Prizes | Probability of taking fourth Prize | Probability Dream Ball target enters | Probability Jirachi enters |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Either | 2.50 | 0 | 0 | 0 |
| 1 | Greedy first | 2.50 + q | q | 1 − q | q |
| 1 | Dream first | 2.50 | 0 | 1 | 0 |
| 2 | Either | 2.50 + q | q | 1 | q |

For **one free slot**, Greedy-first is worth `q` additional expected Prizes under a Prize-only objective, i.e. 0.25 with composition-only or 0.50 with exact positional knowledge.

For **zero or at least two free slots**, neither processing order has any additional expected-Prize advantage under the modeled conditions.

### Why zero slots still averages 2.50 Prizes

Even with a full Bench, Greedy Dice can still take one additional Prize on heads. The fourth Prize requires Jirachi to enter the Bench and trigger Wish Upon a Star. That follow-up cannot occur when the Bench is full, so the total Prize expectation is the original two plus the `1/2) chance of one Greedy bonus Prize.

### Why two slots remove the conflict

The earlier sibling can consume one Bench slot and still leave room for the later sibling.

- Greedy first: if Jirachi is selected, it takes one slot and one more Prize. Dream Ball later uses the second slot.
- Dream first: its target takes one slot, leaving space for a subsequent Greedy-selected Jirachi.

The resulting board can contain both Pokémon, and both orders have the same final Prize distribution.

### Optional Jirachi choice at one slot

In the Greedy-first branch, the player can decline Jirachi's optional Bench-entry Ability after taking it as an extra Prize. Doing so allows Dream Ball to use the only Bench slot. The physical test verifies that **Greedy-first with Jirachi declined reproduces the entire Dream-first metric vector** at one free slot.

If the Dream Ball target is worth `v` Prize-equivalent utility units, the order advantage under an optimal optional-Jirachi policy is:

`q * max(0, 1-v)`

with one free Bench slot, and zero with none or at least two. This formalizes a pure contention effect between alternative occupants.

## Physical validation

The regression creates genuine materialized states at three Bench occupancies while retaining the normal five-slot capacity:

- 0 free: an extra Basic is inserted onto the fifth Bench position;
- 1 free: the original physical fixture is unchanged;
- 2 free: an existing Bench Basic is moved into hand.

All existing card-class totals remain conserved, and no counterfactual merely changes the Bench-limit setting. The same `PrizePendingBatchOrder`, Greedy Dice Item resolution, Jirachi nested additional Prize, and Dream Ball typed deck search are then executed for each world.

The code validates **48 main combinations** of occupancy, order, knowledge and physical coin/layout worlds, plus **8 optional-decline checks**, for 56 conserved execution branches. All expected results are asserted using exact `fractions.Fraction`.

## Scope

The finding concerns this exact two-card Prize award and one available Dream Ball target. It assumes the owner's choice of Greedy Dice/Dream Ball sibling resolution order extends from the known official simultaneous Chansey/Dream Ball ruling; that particular pairwise extension has not yet been directly ruled in the sources located.

It does not evaluate real deck Bench occupancy distributions, opportunity costs of the existing Bench Pokémon, probabilities of acquiring the setup, or downstream opponent retaliation. Those considerations can change whether a one-slot contention state is frequent or desirable.

The broader modeling point is that a single aggregate average Bench occupancy is insufficient to value ordering-sensitive Prize effects. Their utility depends on the discrete count of available slots at the exact resolution moment.

## Reproduction

`python tools/e31_bench_capacity_value.py`.
