# Aichi 2026 Raichu/Electrode: first-turn natural evolution-base seed

**Competitive deck:** [Shu Hosoda, 2026 Aichi Open League fourth-place 60](../../decks/raichu-electrode-aichi-2026/), based on the [published list](https://www.limitlesstcg.com/decks/list/26812).

This source-verified **natural material bound** isolates whether the opening seven cards plus one ordinary first-turn draw contain two distinct Basic Pokémon capable of later becoming Electrode-GX and Alolan Raichu. It is conditional on a valid Basic-containing opening seven, with no extra mulligan draw or other card effects. The six face-down Prize cards are marginalized exactly; conditioning on a valid opening seven, the first turn's draw is uniform among the 53 remaining physical cards.

## Source-checked mechanics

The representative 60-card list contains two Voltorb, one Pikachu, one Ditto Prism Star, nine other Basic Pokémon, and 47 non-Basic cards. Voltorb normally evolves into Electrode-GX; Pikachu into Alolan Raichu; Ditto Prism Star's Almighty Evolution can evolve into either Stage 1, subject to its own timing and Ability availability. One Ditto cannot satisfy both evolutions simultaneously. The two-source condition therefore is `(Voltorb and (Pikachu or Ditto)) or (Pikachu and Ditto)`.

The supplied advanced manual states that neither player can evolve Pokémon on their first turn. Ditto Prism Star itself says Almighty Evolution cannot be used during its first turn or the turn Ditto entered play. With the published list's represented ordinary evolution route, Electrode-GX plus Alolan Raichu cannot both be evolved and launch Electro Rain on the first turn, regardless of going first or second. **Earliest possible normal own turn is turn 2**, assuming both Basic bases were established on turn 1 and the Evolution Pokémon, acceleration material, and attack Energy are accessible on turn 2.

Klefki `sv1-96` has Mischievous Lock: when in the Active Spot, Basic Pokémon in play have no Abilities other than Mischievous Lock. This suppresses its owner's unevolved Ditto Prism Star Almighty Evolution. Before attempting a Ditto evolution, a Klefki-Active line must remove the suppression or find a different evolution route.

## Exact physical-card probabilities

| Event | Exact conditional probability | Percentage |
| --- | --- | ---: |
| Initial seven contains any Basic (unconditional) | `1 - C(47,7)/C(60,7)` | **83.715595%** |
| Two distinct evolution-source Basics in initial seven, given valid seven | `20595960/323315421` | **6.370237%** |
| Two distinct source Basics after first normal draw, given valid seven | `814128/9797437` | **8.309602%** |
| Native Voltorb and Pikachu both available after that draw, given valid seven | `351120/9797437` | **3.583794%** |
| Two-source condition holds only with Ditto, given valid seven | `463008/9797437` | **4.725807%** |

Of qualifying eight-card natural seed events, **56.871647% need Ditto** to provide one of the two different Stage 1 source Basics. If Klefki is Active throughout the evolution turn and its Ability lock is uninterrupted, these Ditto-dependent states cannot execute Ditto's evolution Ability in that state.

The SFT evaluates both a closed-form combinatorial identity and independent exhaustive hand-multiplicity enumeration. For eight observed physical cards, the two-source event count is:

`C(60,8) - C(58,8) - 2*C(56,7)`.

Divide its probability in a random eight by the probability of a valid initial seven. Any eight-card hand satisfying the two-source condition must have started from a valid seven, since a single subsequent card cannot create two distinct eligible Basic role categories.

## Reproduce

Run `python results/tests/raichu_2026_natural_seed/reproduce.py`, or the repository's dedicated GitHub Actions regression. It authenticates exact deck quantities, print IDs, source evolution chains, Ditto and Klefki ability wording, the advanced manual first-turn rule, and both exact-probability derivations.

**What this estimate does not measure:** actual opening success with 4 Quick Ball, 1 Ultra Ball, 1 Battle VIP Pass, Secret Box, supporter draw, Ability draw, mulligan-bonus draws, and Prize searches. It excludes opponent interaction, turn-two Stage 1 access, five Energy cards reaching discard, Electrode's self-Knock-Out Prize consequences, and Electro Rain attack permission. It cannot be interpreted as full combo setup rate, deck win rate, or a reliable assessment of the deck's tournament strength.

**Next experiment:** couple these physical base identities to a joint search/discard and draw policy, then model turn-two evolution plus the Prize-state-dependent five-Energy Bomb action without double-spending connectors.


## Natural turn-two dual evolution material

The companion SFT `turn2_material.py` includes the two printed Stage 1 counts: **three Electrode-GX and two Alolan Raichu**, in addition to the starting Basic source counts. It tests a stricter natural event:

1. by the end of own turn one, the first eight observed cards contain two different Basic source roles sufficient for Voltorb/Pikachu/Ditto evolution;
2. by the start of own turn two, the first nine observed cards contain **at least one Electrode-GX and one Alolan Raichu**.

This is a prerequisite for the natural turn-two double evolution. Its chronological condition prevents a Basic drawn on own turn two from being incorrectly counted as evolution-eligible. The model assumes the player benches the necessary Basics on turn one and neither player removes them.

| Natural turn-two material condition, given valid starting seven | Exact fraction | Percentage |
| --- | --- | ---: |
| Both source Basics by own T1 and both Stage 1 evolutions by own T2 | `1269021526/222764325069` | **0.569670%** |
| Same with native Voltorb and Pikachu bases | `41327540/17135717313` | **0.241178%** |
| Same relying on Ditto for a source Basic | Difference between fractions | **0.328492%** |

Of naturally complete turn-two evolution-material states, **57.663601% depend on Ditto** for one of the two evolution sources. This makes a live Klefki Active Ability lock a relevant caveat even after both Stage 1 cards are naturally available.

Independent exact oracles agree: one enumerates every legal seven-card hand and two chronological draws; the other enumerates every qualifying first-eight multiset and the physical identities of the possible ninth card. Both marginalize unknown Prizes. The sample space remains a valid initial seven, with no search or draw effects.

**Do not treat 0.569670% as the deck's turn-two attack rate.** The published deck has Quick Balls, Battle Compressor, multiple draw Abilities, search and recovery, and twelve Special Energy. The attack also needs Energy available and Electrode-GX to be activated in a compatible Prize state. The statistic shows how strongly the list depends on those action channels to assemble the target state.


## Physically paid Quick Ball-only first-turn base-access ceiling

The `quick_ball_upper.py` SFT introduces **all four actual Quick Ball copies** from the published deck. It enumerates **68,462 weighted hand/Prize/draw class configurations** conditional on a valid initial seven, accounting for the six Prized physical copies, exact remaining Basic targets in the deck, the starting Active drawn from the initial seven, and distinct Quick Ball discard payments. Searches move the selected Basic from deck to hand, and subsequent Bench placement is represented.

| First-turn access scenario | Exact fraction / probability |
| --- | --- |
| Natural source Basics only | `814128/9797437` = **8.309602%** |
| Natural sources + up to four Quick Ball searches, all legal discard payments allowed | `80313436404203/265089546832110` = **30.296719%** |
| Same, while preserving all source-role Basics and remaining Quick Balls as discard targets | **30.296719%** in this particular coarse card-class model |

This **3.65× multiplicative material-reachability gain** shows that Quick Ball meaningfully changes first-turn access even before considering Ultra Ball, Battle VIP Pass, Secret Box, draw Abilities or card-effect searches. The script validates its natural-only subtotal independently against the separate eight-card closed-form oracle, and asserts distinct-card discard-cost counterexamples.

**Upper-envelope conditions:** the planner chooses the starting Active and Quick Ball action sequence optimistically with knowledge of the physical six-Prize configuration. In an actual game, the starting Active is chosen before deck inspection, and discard choices incur strategic opportunity costs. The `filler_only` policy protects target source Basics and other Quick Balls, but treats every other 52 physical cards as a potential cost, including important Trainers, attackers and Energy. Equal measured outcomes across those two policies do not imply that a rational tournament player can always afford the payments. Every source remains subject to Bench position, Klefki suppressing Ditto later, deck-search lock, and the need to evolve and accelerate Energy on turn two.

This is a verified **first-turn two-evolution-source access ceiling for one deliberately limited Item channel**, with no claim about whole-deck setup success or match outcomes.


## Sensitivity to discard preservation: twelve actual Special Energy

The `quick_ball_energy_sensitivity.py` companion refines the 43-card generic `other` class into **12 printed Special Energy** (4 Reversal, 4 Counter, 4 Unit Energy LPM) plus 31 remaining non-Basic non-Quick-Ball cards. It exhaustively evaluates **799,953 physically weighted seven-hand/six-Prize/first-draw configurations** with the same optimized Active choice and sequential paid Quick Ball transitions.

| Hypothetical permitted Quick Ball discard payments | First-turn two-base accessibility |
| --- | ---: |
| Energy cards only | **24.074229%** |
| Energy cards or another Quick Ball | **25.003751%** |
| Any physically legal discard target | **30.296719%** |
| No Quick Ball (natural draw only) | **8.309602%** |

The strict Energy-only policy sacrifices 6.22249 percentage points of modeled first-turn base access relative to unrestricted payments. Even so, its 24.07% is nearly three times the natural-only baseline. These are exact combinatorial probabilities under each stated permission policy, not Monte Carlo estimates. A 12-Energy discard pool is concrete and relevant to Electrode-GX, whose ability later attaches from discard, but the actual strategic acceptability of discarding any particular Energy depends on the Prize differential, remaining copies, timing, and intended Electro Rain payload.

This captures one measurable implication of state-dependent discardability (DCI) and connector opportunity cost: identical four-Quick-Ball access paths yield distinct feasibility after the permitted cost cards change. Full-card strategic preservation, draw/search sequencing, Ability lock, and opponent actions remain unmodeled. In particular, treating every other card as protected is a deliberately conservative discard policy, **not** an experimentally established optimal Pokémon TCG policy.

Reproduction: `python results/tests/raichu_2026_natural_seed/quick_ball_energy_sensitivity.py`. Independent boundary tests in `quick_ball_upper.py` confirm a played Quick Ball cannot pay its own discard cost and that discarding another Quick Ball sacrifices its future use.
