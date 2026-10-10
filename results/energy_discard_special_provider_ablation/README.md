# Exact provider ablation: Double Dragon versus Double Colorless Energy

## Question

What physically causes the continuation-reversal phenomenon: merely having one two-unit Special Energy card, or that card's **flexible typed provision**?

A matched-provider ablation isolates the cause. We replace one attached Double Dragon Energy (DDE) with one Double Colorless Energy (DCE), holding its *physical card count and Energy unit count* fixed.

## Controlled source cards

- Double Dragon Energy, Roaring Skies `xy6-97`: provides two units of every Energy type while attached to a Dragon Pokémon.
- Double Colorless Energy, Next Destinies `bw4-92`: provides two Colorless units.

Both are Special Energy cards in the bundled Expanded-legal snapshot. The hypothetical attacker is a Dragon Pokémon for the DDE case, and it has exactly three additional Basic Energy cards. The future desired attack costs exactly three symbols from the nine Basic Energy types plus Colorless. A preceding attack discards two generic Energy units, so either DDE or DCE can be a one-card payment.

## Exact set identity

Let `B` be any multiset of three Basic Energy cards, and `C` be any three-symbol future attack cost. Let `ready(E+B,C)` denote ability to pay the cost using the specified provider plus the three Basics.

**Identity 1.**

`ready(DCE+B,C) == ready(B,C)`.

Proof: DCE contributes only Colorless units. Any colored requirements that were satisfied before must already have been covered by Basics. The three Basics can supply the remaining Colorless symbols because every Energy type pays Colorless attack costs, and the total cost is exactly three. The reverse implication follows trivially by adding DCE.

**Identity 2.**

`ready(DDE+B,C) and not ready(B,C)`

is exactly the set of initial DDE states where paying a two-Energy discard with DDE alone destroys immediate next-attack readiness.

Together, these identities mean that **the configurations in which DDE enables a new three-Energy attack cost relative to DCE are precisely the configurations in which discarding DDE alone loses that ability**.

## Exhaustive result

All 220 unordered three-symbol attack-cost multisets were crossed with all 165 unordered three-Basic attachment-type multisets, for 36,300 configurations:

| Metric | Exact count |
| --- | ---: |
| DDE states initially able to pay cost | 24,468 |
| DCE states initially able to pay cost | 1,140 |
| Three Basics alone able to pay cost | 1,140 |
| Additional states enabled by DDE typed flexibility | 23,328 |
| DDE states where one-card DDE payment loses readiness | 23,328 |
| DCE states where one-card DCE payment loses readiness | **0** |

In every DDE-initially-ready state, discarding two Basics can preserve the desired three-unit cost. In every DCE-initially-ready state, discarding DCE alone leaves three Basics capable of paying it.

The **zero** DCE reversals are a structural result of the controlled three-Basic supply and three-unit future cost. This result says nothing about turn sequencing, the legality of a specific different attack, or objective-specific value of Energy cards.

## Source-backed witness interpretation

For Regidrago VSTAR's Grass/Grass/Fire cost and Basic Grass/Fire/Fire attachments, DDE makes the attack ready but DCE does not. The ablation is a controlled hypothetical provider replacement, not an assertion that the DCE version could first execute Apex Dragon in that state. For the single Basic triple Grass/Grass/Fire, either Special Energy provider starts ready; discarding DCE alone preserves this typed cost.

This establishes why physical-card and raw-unit matching can give incorrect generalized dominance results: types determine which cost states exist, and those same types can disappear when the flexible provider is discarded.

## Reproduction

`tools/energy_discard_special_provider_ablation.py` verifies printed Energy-card source text, enumerates 36,300 cost/mix pairs, runs the attack-cost-aware exact Energy matcher, and asserts both the identities and every aggregate.

Run `python -m tools.energy_discard_special_provider_ablation` from the repository root.

The current solver correctly treats Colorless *cost symbols* as wildcards while keeping the strict typed Energy discard matcher distinct. No global solver modification is needed.

## Limitations

These are deterministic comparisons of type configurations under an always-active DDE provider on a Dragon Pokémon. They are neither gameplay frequencies nor tournament card recommendations. Special Energy control, manual attachments, recovery, Bench, and damage are omitted. The result connects to [continuation synthesis](../energy_discard_continuation_synthesis/) and the original [Regidrago witness](../energy_discard_continuation_frontier/).
