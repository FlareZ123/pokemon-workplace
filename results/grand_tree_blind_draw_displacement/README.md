# Blind draws reduce deck-only Grand Tree evolution searchability

## Why this matters

The preceding Grand Tree setup-zone probabilities measure the chance
that both required evolution stages remain in the deck immediately
after opening hand and Prizes are dealt.

Grand Tree's own text forbids evolving a Basic during its controller's
first turn. In a normal subsequent turn, the player takes a mandatory
turn-opening draw before using Grand Tree. That draw moves a card from
the deck into the hand. If it is the only Stage 1 or Stage 2,
Grand Tree's **deck-only search route** loses that card.

This investigation quantifies the effect of `d` additional
**ordinary blind draws**, with no subsequent card movement, searches,
recovery, card effects or deck reshuffles affecting category
frequencies. It makes no claim about the broader strategic value of
drawing an evolution card.

## Exact model

Condition on a particular Basic already among the opening seven:
of the other `N=59` cards, six are in the rest of opening hand,
six are Prizes, and 47 initially remain in the deck.

After `d` blind draws from deck, the number of inaccessible cards
for Grand Tree's own search is `u=12+d` and the searchable deck
has `47-d` cards, with `0<=d<=47`.

With `a` Stage 1 copies and `b` Stage 2 copies:

```text
q_d(k) = C(12+d,k) / C(59,k)

P(both stages remain searchable after d draws)
       = 1 - q_d(a) - q_d(b) + q_d(a+b).
```

For singletons at each stage:

```text
P(both remain in deck after d draws)
       = (47-d)*(46-d) / (59*58).
```

Given at least one singleton Stage 1 remains in deck, the singleton
Stage 2 is also still there with probability `(46-d)/58`.

These exact identities assume uniformly random blind draws and a
uniformly randomized initial deck allocation.

## Quantitative effect

| Additional blind draws | 1/1 stage pair searchable | 2/2 stage pair searchable |
| ---: | ---: | ---: |
| 0 | 63.1794% | 92.3940% |
| 1 | 60.4909% | 91.0396% |
| 2 | 57.8609% | 89.5829% |
| 3 | 55.2893% | 88.0264% |
| 5 | 50.3214% | 84.6258% |
| 8 | 43.3080% | 78.8553% |
| 10 | 38.9246% | 74.6055% |

For the singleton pair, the first blind draw changes the probability
from `1081/1711` to `1035/1711`, a loss of
`46/1711` or approximately **2.6885 percentage points** in
*deck-only* joint searchability.

This does not mean drawing a Stage 1 or Stage 2 is bad. A card drawn
to hand might be available for natural evolution or another effect,
and extra draw may increase the chance of finding Grand Tree itself.
The probability here isolates the deck-search branch that can be
hidden by a less precise consistency metric.

## Reproduction

`python results/grand_tree_blind_draw_displacement/reproduce.py`

The checks include:

- exact singleton formulas for every `d=0..47`;
- finite-population bounds and draw-exhaustion guard;
- monotonic deck-only availability with increasing draws;
- exact conditional Stage 2 availability after Stage 1 remains;
- independent multivariate hand/Prize allocation enumeration across
  192 positive Stage1/Stage2-copy and draw-count cases.

## Scope

The model assumes no other card movement between opening setup and
the eventual Grand Tree activation except `d` blind draws. Full
playability also needs Stadium access, Basic in play, turn restrictions,
turn order, card legality, Prize knowledge, opponent interference,
alternative evolution actions, and strategic sequencing.

Grand Tree is an ACE SPEC. Its availability as the Stadium itself is
not included in these stage-only probabilities.

## Conclusion

Initial setup-zone probabilities are a useful reproducible benchmark,
but realistic timing can change the physical deck zones before a
source action becomes available. Modeling **when** a card is drawn or
searched is necessary before turning a static deck-access statistic
into a recommendation.
