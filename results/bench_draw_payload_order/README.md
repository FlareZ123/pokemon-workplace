# Crobat V and Dedenne-GX: staged draw, singleton retention, and Bench debt

## Question and source card text

A hand-to-Bench support trigger may be executable while its **actual draw payload** changes whether an important singleton survives.

The bundled card pool gives:
- Crobat V `swsh3-104`, **Dark Asset**: when played from hand onto the Bench, optionally draw up to six cards in hand.
- Dedenne-GX `sm10-57`, **Dedechange**: when played from hand onto the Bench, optionally discard the remaining hand and draw six.
- Each Ability has a once-per-turn, same-name restriction. Each Pokémon gives up two Prize cards if Knocked Out.

The Advanced Player's Rulebook supports the hand-entry timing, optional effects and five-Pokémon Bench limit. This experiment assumes both entries are legal when sufficient Bench capacity exists.

Code: [model](../../tools/bench_draw_payload_order.py) and [independent physical-list reproducer](reproduce.py).

## Controlled, exact state

The deck contains 60 cards. A valid seven-card opening includes Crobat V, Dedenne-GX and a different Basic selected as Active. The singleton target K is **absent from the opening hand**. Six cards are Prized; the turn begins with one normal draw. The player then spends non-target cards without looking at or altering the deck until the hand contains h cards, preserving Crobat V and Dedenne-GX and any drawn K.

The target is uniformly distributed over the **53** originally unseen cards: one normal draw position, six Prize positions, and 46 remaining live deck positions. The modeled policies observe the current hand and the result of each draw, without inspecting hidden Prize or deck positions. There are at least two free Bench slots. Success means K is in hand when the policy stops. Discarded K cannot be recovered in this restricted action window.

If Crobat V is benched from a hand containing h cards, it draws **a = max(0,7-h)** cards, because its Bench entry first reduces hand size by one. Dedenne-GX draws six after resetting the rest of the hand. With this 46-card draw pool, both stages can draw their full widths for h=3..7.

## Policies and result

| Action policy | Final K probability, exact | At h=5 |
| --- | ---: | ---: |
| Dedenne immediately even if K is held | 6/53 | 11.320755% |
| Dedenne only if K is missing | 7/53 | 13.207547% |
| Crobat only if K is missing | (1+a)/53 | 5.660377% |
| Crobat then mandatory Dedenne | 6/53 | 11.320755% |
| Crobat; if K is still missing, use Dedenne | (7+a)/53 | **16.981132%** |

A forced Crobat-then-Dedenne sequence can discard K if it appeared in the normal draw or Crobat's draw, eliminating the apparent value of the first draw for a *final-hand* singleton objective. At h=5 that forced policy discards K on **3/53** target positions. The adaptive staged policy discards K on zero target positions because it skips Dedenne when K has been found.

The conditional Dedenne-alone policy already preserves K if it appeared in the normal draw. The staged policy's incremental benefit is exactly **a/53**.

## Hand-size sensitivity and cost

| Initial hand h | Crobat draw a | Conditional Dedenne | Adaptive staged | Gain | Extra expected Bench occupants |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 4 | 13.207547% | 20.754717% | 7.547170 pp | 0.905660 |
| 4 | 3 | 13.207547% | 18.867925% | 5.660377 pp | 0.924528 |
| 5 | 2 | 13.207547% | 16.981132% | 3.773585 pp | 0.943396 |
| 6 | 1 | 13.207547% | 15.094340% | 1.886792 pp | 0.962264 |
| 7 | 0 | 13.207547% | 13.207547% | 0.000000 pp | 0.981132 |

The conditional staged policy uses (52-a)/53 **more** Bench slots on average than Dedenne alone. At h=5 its expected Bench occupancy is 102/53, compared with 52/53 for conditional Dedenne alone. Without two free slots or a pickup effect, the two-entry staged line is inaccessible.

As an illustrative scalar toy objective, value retaining K at V and assign penalty C for an additional support body on the Bench. The staged policy wins only when **C/V < a/(52-a)**, provided a>0. For h=5, C/V must be less than **4%**. This penalty is hypothetical and is not a measured Prize-exchange or win-rate parameter.

## Evidence and reproducibility

The model enumerates each possible singleton location and simulates hand size, target retention/discard, Bench entries, Dedenne activations and draw count. The separate reproducer independently manipulates **literal lists of hand, deck, Bench and discard cards**; it agrees with the primary model across four live-deck sizes and six hand sizes, for all five policies. A separate closed-form expression agrees whenever the draw pool has at least a+6 cards.

The h=5 60-card regression verifies, as exact fractions:
- conditional Dedenne 7/53; adaptive staged 9/53;
- forced two-support draw 6/53 and target discard 3/53;
- adaptive staged expected Bench entries 102/53;
- adaptive staged Dedenne uses 50/53;
- adaptive staged total cards drawn 404/53.

Run `python results/bench_draw_payload_order/reproduce.py` on Python 3.11+.

## Strategic interpretation and limits

The number of cards drawn over a sequence is not a reliable substitute for final-hand resource reachability. Dedenne's reset can discard precisely the singleton that Crobat just found. Preserving the option to stop after the first draw is therefore strategically meaningful.

The additional two-Prize Bench occupant can have substantial matchup-dependent cost. The model does **not** estimate that cost, deck win rates, or the chance of opening with both supports. It excludes Quick Ball discard payment, items played between draws, other Abilities, Ability/Item lock, pickup, recovery, opponent turns, alternate draw resources, and any positive value of having K in the discard pile. A more complete study could embed these payload transitions into the existing paid Quick Ball Bench-action planner, with state-dependent protected-card valuation and physical support-card occupancy.

## K0/K1 information ablation: suppressing doomed support entries

A separate controlled extension supplies a `prize_known` switch. In ordinary **K0**, the singleton K may be in the unknown six Prizes, so the player cannot skip a draw just because K actually is Prized. In **K1**, a prior physical deck search has established that K is among the remaining face-down Prizes by inspecting all remaining deck contents. K1 reveals **composition**, not the face-down Prize position.

Holding the material hand and deck distributions fixed isolates the *information benefit* of recognizing that a draw cannot find Prized K. The goal-directed conditional policies skip draw Abilities in those known-Prized states. Because K cannot be reached by the modeled draws in either case, final retention probabilities are unchanged.

At h=5, with the same 53 original singleton positions:

| Quantity | K0 (unknown Prizes) | K1 (known composition) |
| --- | ---: | ---: |
| Conditional Dedenne target retention | 7/53 | 7/53 |
| Conditional staged target retention | 9/53 | 9/53 |
| Conditional Dedenne expected Bench entries | 52/53 | **46/53** |
| Conditional staged expected Bench entries | 102/53 | **90/53** |
| Conditional staged expected Dedenne activations | 50/53 | **44/53** |
| Staged extra Bench entries over Dedenne | 50/53 | **44/53** |

A previously established K1 state therefore avoids **6/53** unnecessary Dedenne-only entries, or **12/53** unnecessary staged support entries, with zero reduction in the narrow K-retention objective. In the illustrative scalar occupancy model, the staging threshold becomes `C/V < a/(46-a)`, or about **4.545%** at h=5, rather than the K0 threshold of 4%.

**Scope warning:** This is an information-only paired-state ablation. Acquiring K1 normally requires an actual deck search, whose card costs, sequencing, and state changes are *not* charged here. Dedenne or Crobat might still be worth using to draw other valuable cards even when K is Prized. The conclusion concerns the singled-out K objective and the additional option that deck inspection supplies. The independent physical-list regression now validates both knowledge conditions.
