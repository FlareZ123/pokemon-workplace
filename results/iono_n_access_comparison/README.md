# Iono versus N: exact local target-access reversal

## Question

Paper Expanded contains two Supporters with superficially similar Prize-dependent redraws: N shuffles both players' hands into their decks, while Iono puts both shuffled hands at the bottoms of their decks. When does the destination reverse the probability of drawing a useful card?

Card-text witnesses in the bundled database: Iono `sv2-185` and N `bw3-92`.

## Exact model

Fix one player's pre-Supporter state. Let D be cards in the preexisting deck, H cards in that player's current hand, K useful interchangeable outs in the deck, R useful outs in the hand, d their remaining Prize cards, and Q the opponent's hand size. Assume the old deck's order is exchangeable and all K+R outs are equivalent for the immediate objective.

**N:** Regardless of hand emptiness, the player's fresh hand has at least one out with probability

`P_N = 1 - C(D+H-K-R,d)/C(D+H,d)`,

with draw count capped to available cards and impossible failure combinations counted as zero.

**Iono:** If both H and Q are zero, the conditional draw never happens. Otherwise, when d ≤ D,

`P_Iono = 1 - C(D-K,d)/C(D,d)`.

When d exceeds the preexisting deck, the draw exhausts it and continues into the randomized returned hand. The exact kernel handles that boundary as well.

These equations give **conditional one-step access probabilities**. They do not rank these two Supporters over a complete game; opponent effects, legality and future value remain outside the comparison.

## Opposite signs under one fixed deck geometry

For D=46 preexisting deck cards, H=5 old-hand cards, d=6 remaining Prize cards, Q=2 opponent-hand cards and **eight total interchangeable outs**:

| Outs in old hand R | Outs in original deck K | Iono at least one out | N at least one out | Iono minus N |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 70.527017% | 66.148602% | **+4.378415 pp** |
| 1 | 7 | 65.168292% | 66.148602% | **-0.980309 pp** |
| 2 | 6 | 59.021521% | 66.148602% | **-7.127081 pp** |

The source of the reversal is the distribution of outs across hand and deck. Iono initially excludes the old hand from the immediate draw, increasing the concentration of deck-native outs, while N recycles the whole hand into the randomized draw pool.

At H=5 and **exactly one old-hand out**, Iono overtakes N in the six-draw window once there are at least **nine deck outs**. The exact break-even first K as a function of d=1..6 is 10, 10, 9, 9, 9, 9. These high-density boundary examples show that the value of a returned hand card depends on how saturated the deck already is with alternative outs.

## Coupled conditional draw

Iono's draw is enabled when either player puts cards on deck bottom. For a player with H=0, Q>0 and d≤D, Iono's own target access equals N's under this local exchangeable-deck projection. If **both players' hands are empty**, Iono's draw is suppressed, while N's Shuffle/Draw text has no such conditional gate. In the real game, a Trainer card must also be legally playable and its effect must change the state; this comparison is a conditional transition model.

## Validation

- `tools/iono_n_access_comparison.py` uses exact fractions and the existing `hand_return_payment_frontier.hit_probability`.
- `results/iono_n_access_comparison/reproduce.py` independently enumerates all labeled configurations of small decks and hands, allowed useful-out compositions, Prize-draw sizes, and empty/nonempty opponent hands, including draws that cross into the bottomed hand.
- Tests assert the source print text, numeric reversal, empty-hand gating, and six Prize-count thresholds.

The resulting model is especially useful for K0/K1-aware sequencing: after a deck search reveals which outs remain in the deck, the relative immediate access of bottom-return and shuffle-return redraws may change sharply.
