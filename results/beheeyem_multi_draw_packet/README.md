# How extra T3 draws overcome a recycled Beheeyem / TAE packet bottleneck

## Question

[Two-turn packet recycling](../beheeyem_two_turn_packet_recycle/) established that a Beheeyem `sm11-91` Mysterious Noise attack can return its Stage 1, underlying Elgyem, and attached Triple Acceleration Energy `sm10-190` to the deck. With only one natural T3 draw, however, the probability of accessing another complete packet is extremely low. A deck with singleton Beheeyem and singleton TAE has a strict impossibility: that one draw cannot retrieve both distinct missing cards.

This experiment varies the number of **blind T3 cards drawn** from 0 through 5, under the same physically conserved game-state assumptions. It quantifies the discrete benefit of overcoming multi-category packet contention, without assuming specific draw Supporters or Abilities are available.

## Physical state and exact calculation

The baseline is exactly the preceding experiment: two mature Elgyem and partner Basic are already in play by T1; the other six cards in hand by T2 are drawn uniformly from 57 residual cards containing `B` Beheeyem, `T` TAE and filler; six of the 51 unseen are Prizes, leaving a 45-card deck. A first T2 Mysterious Noise uses one Beheeyem and one TAE from hand and shuffles both plus its underlying Elgyem into the deck, leaving **48** randomized cards from which the T3 player draws `d` cards without replacement. Remaining B/TAE in hand count toward the second packet.

For each T2 hand composition `(b,t)`, the exact probability is weighted by

\[
\frac{\binom{B}{b}\binom{T}{t}\binom{57-B-T}{6-b-t}}{\binom{57}{6}}.
\]

For each possible Prize composition `(p_B,p_T)`, weight by the corresponding multivariate hypergeometric distribution of six Prizes among 51 unseen. The returned physical packet makes the T3 deck contain

\[
D_B=B-b-p_B+1,\qquad D_T=T-t-p_T+1
\]

Beheeyem and TAE respectively, and exactly 48 cards in total.

If the T2 attack exhausts both B and TAE from the hand, the probability of finding **at least one of each** in `d` T3 draws is the inclusion-exclusion expression

\[
1-\frac{\binom{48-D_B}{d}+\binom{48-D_T}{d}-\binom{48-D_B-D_T}{d}}{\binom{48}{d}}.
\]

If only one category is missing, the expression reduces to the probability of drawing at least one from that category. If both are already in hand, the packet remains available with probability one. All calculations use exact rational arithmetic.

This is a **conditional packet supply model**. It assumes that the two Elgyem are mature, that their evolution and attachment are otherwise legal, and that the second one can become Active. It does not model how any draw effect is paid for, Supporter limits, discards, opponent responses, searching or later-turn Energy sourcing.

## Results with four Beheeyem and four TAE

The first T2 packet is available in **12.006938%** of the conditioned six-card-hand cases regardless of the T3 draw budget.

| Number of T3 cards drawn | Probability of both T2 and T3 packet access | T3 packet conditional on T2 packet |
| ---: | ---: | ---: |
| 0 | 0.123225% | 1.02628% |
| 1 | 0.316352% | 2.63474% |
| 2 | **0.608267%** | 5.06597% |
| 3 | 0.979864% | 8.16082% |
| 4 | 1.414259% | 11.77868% |
| 5 | 1.896601% | 15.79587% |

Increasing T3 access from one to two blind draws **nearly doubles** the two-packet rate (0.316352% to 0.608267%). Moving from one to five draws multiplies it approximately sixfold. This is an exact short-horizon result, although five draws cannot be assumed freely available in a competitive deck.

## Singleton threshold and copy-count sensitivity

A single Beheeyem and a single TAE cannot be reacquired from the shuffled deck in **one** draw after both have been spent. With two draws, a complete packet becomes possible:

- The first T2 packet incidence is exactly `5/532`.
- After the attack returns one B and one T, the probability that two T3 cards are precisely those two identities is `1 / C(48,2) = 1/1128`.
- The unconditional consecutive-packet incidence is therefore **`5/600096`**, or **0.000833200%**.

| B / TAE copies | T3 draws = 1 | T3 draws = 2 | T3 draws = 5 |
| --- | ---: | ---: | ---: |
| 1 / 1 | 0% | 0.000833% | 0.008332% |
| 1 / 4 | 0.007920% | 0.025489% | 0.127728% |
| 2 / 2 | 0.013924% | 0.033981% | 0.147613% |
| 3 / 3 | 0.093180% | 0.193469% | 0.683733% |
| 4 / 4 | 0.316352% | 0.608267% | 1.896601% |

The scan reveals strongly **nonlinear draw value**, especially at the boundary where the hand is missing two independent card categories. It also supplies a controlled example of balancing raw packet redundancy and draw volume: with three copies of each packet card and five T3 draws, packet incidence exceeds the four-copy-per-card result with two T3 draws. The simulated draw counts are not assumed to be achievable without spending or discarding other resources.

## Validation

- `tools/beheeyem_multi_draw_packet.py` computes the exact joint hand/Prize/draw hypergeometric probabilities for 1–4 copies of each packet card and 0–48 draws.
- `reproduce.py` asserts symmetry, monotonicity in draw budget, the previous one-draw exact results across five copy-count settings, and the singleton `5/600096` threshold. It emits 35 sample results across five B/TAE configurations and seven draw budgets.
- `monte_carlo.py` independently shuffles real 57-card conditioned pools, removes six Prizes, physically returns the T2 packet to a 48-card shuffled deck, and samples successive T3 cards. With 750,000 four/four and 500,000 two/two simulations, it checks all 0–5 draw budgets against the exact values.

The next step is to connect `d` to actual Expanded card effects and budgets. Extra draw actions can compete with the same Supporter needed for Energy or Evolution access, or require discarding strategically protected cards. The hypergeometric frontier is best used as a **component in a larger action-realism model**.
