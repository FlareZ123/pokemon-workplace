# Aichi champion Radiant Eternatus launch: cost of preserving discard resources

## Question

The existing [exact Aichi Shadow Rider launch baseline](../shadow_rider_radiant_launch/) reports a **43.699162430%** first-going-second-draw chance to put two Shadow Rider Calyrex VMAX from the deck onto the Bench via Radiant Eternatus in its restricted direct/Treasure access model. It treats Mysterious Treasure's discard of one additional hand card as freely affordable. How sensitive is that number to explicit *strategic* willingness to discard one card?

The [complete 60-card Aichi-winning list](../competitive_deck_baselines/) supplies exactly 1 Radiant Eternatus, 4 Shadow Rider Calyrex VMAX, 4 Mysterious Treasure, 13 other opening-eligible Basics, **11 Psychic Energy**, and 27 other cards. The event was the [10 May 2026 CL Aichi Open League](https://www.limitlesstcg.com/tournaments/566/decklists), won by Yasunori Kato.

The implementation is [`tools/shadow_rider_treasure_discard_sensitivity.py`](../../tools/shadow_rider_treasure_discard_sensitivity.py), with [reproduction test](reproduce.py).

## Rules and baseline scope

Mysterious Treasure is an Item searching the deck for a Psychic/Dragon Pokémon after discarding one other card from hand; Radiant Eternatus's Climactic Gate puts up to two Pokémon VMAX from the deck onto the Bench and ends the turn. Card source and route conditions are checked in the original [Radiant launch baseline](../shadow_rider_radiant_launch/). The present extension preserves its opening generation, six hidden Prizes, one natural draw going second, non-Radiant opening Active requirement, and need for at least two remaining VMAX cards *in the deck*.

The opponent supplies no disruption. There are no bonus opponent-mulligan draws, supporters, extra search connectors, or additional turns. All percentages are conditional on a Basic-valid opening seven. A draw of another non-Radiant Basic on the first turn cannot retroactively change a Radiant-only starting Active.

**Every listed discard restriction below is a hypothetical conservation policy, not a mechanical restriction.** Discarding other cards remains legal under Mysterious Treasure. These restrictions measure how often a player could execute this line *while respecting a chosen resource-preservation discipline*. This does not establish which discipline maximizes eventual win probability.

## Exact results

The directly held Radiant route contributes **12.017840120%** under every policy, since it does not need Mysterious Treasure. The Treasure route has the following separate probabilities:

| Permitted Treasure payment, with one Treasure consumed | Treasure-route two-VMAX launch | Total with direct Radiant |
| --- | ---: | ---: |
| Any remaining hand card (free-payment upper envelope) | 31.681322310% | **43.699162430%** |
| At least one Psychic Energy in hand, discarding one | 24.843972088% | 36.861812209% |
| At least two Psychic Energy in hand, discarding one and keeping one | 12.119810755% | 24.137650875% |
| A second Mysterious Treasure copy in hand | 5.647244745% | 17.665084865% |
| Psychic Energy **or** a spare Treasure | 26.390181773% | **38.408021894%** |
| At least two Psychic Energy **or** a spare Treasure | 16.072588787% | **28.090428907%** |
| At least two Psychic Energy, a spare Treasure, **or** a VMAX in hand | 22.916019372% | **34.933859492%** |

The free-payment and two-Energy-or-spare-Treasure totals differ by **15.608733523 percentage points**. This is a sensitivity interval between stated policies; it must not be read as a measured gameplay penalty.

The VMAX-in-hand option is available only when at least two VMAX remain in the deck for Climactic Gate. It sacrifices a card that might otherwise evolve a Shadow Rider Calyrex V in a later turn, so the option is strategically conditional. Discarding Psychic Energy has its own future cost because this deck's Underworld Door Ability accelerates Psychic Energy from the hand.

The `at least two Energy` guard implements one narrow prospective conservation heuristic. The launch ends the current turn, so the preserved Energy is for *later* turns and its actual value depends on future draw, Knock Outs, and matchup conditions. The count of Psychic Energy alone does not establish a card's DCI.

## Computation and validation

The model uses six categories of physical card copies, with counts `(1,4,4,13,11,27)`. Every valid seven-card opening class, six-Prize allocation, and first-draw category is weighted by its multivariate hypergeometric multiplicity. All numerators and denominators are arbitrary-precision integers, converted to reduced `Fraction` probabilities. No Monte Carlo estimation is used.

Checks include:

1. The exact original five-category direct and free-payment route fractions must match **bit-for-bit**.
2. The full deck's named Pokémon, Trainer and Energy counts must match the six category totals.
3. An independent enumeration of **18,312 labeled physical toy-deck deals** with opening size three and two Prizes must match every grouped probability across all eight route/payment classes.
4. Monotonic policy inclusion checks and exact locked fraction checks for the representative Energy, spare-copy, and VMAX branches.

## Competitive interpretation and next work

The source deck's four Mysterious Treasure copies provide strong theoretical access to Radiant Eternatus. Whether that access is *realistically attractive* depends on which resources can be sacrificed at that moment. The 11 Psychic Energy cards create many mechanically payable lines, yet those Energy cards also help fuel Underworld Door in later turns.

A useful next step is a multi-turn decision model that carries the discarded card's identity forward. It should score subsequent Underworld Door availability, hand size, VMAX evolution access, rival Mysterious Treasure targets, opponent Ability/Item locks, and the three-Prize liability of each VMAX. Such a model can compare preserving a protected singleton versus paying for the immediate two-VMAX launch using terminal game utility.

Until then, these are **exact conditional opening-access sensitivities** for a known winning deck, without estimates of match win rate.
