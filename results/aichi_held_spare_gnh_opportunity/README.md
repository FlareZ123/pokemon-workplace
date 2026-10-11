# Natural Aichi opportunity for paid duplicate TM + Jet searches

## Question

The [Aichi G&H action-completeness counterexample](../gnh_optional_paid_duplicate_search/)
requires a player who already holds one Technical Machine:
Evolution and one Jet Energy, yet can find spare copies of
both through G&H's optional two-card payment.

How often can that **physical named-resource configuration**
arise naturally, without an earlier card search, in the
published 2026 Aichi runner-up Vileplume deck?

## Event definition

Use the source deck's 60 cards, with 14 eligible Basic starters,
one Jirachi, four Guzma & Hala, two TM: Evolution, two Jet Energy,
and two Artazon. All other cards occupy a 49-card residual
category. The deck follows ordinary seven-card opening, six
random Prize cards, and one natural turn draw.

Condition on the seven-card opener containing a Basic Pokémon.
Count only states with:

1. The unique Jirachi in the **opening seven**, so it may
   be chosen as the starting Active Pokémon.
2. At least one G&H among the opening seven plus the one
   subsequent natural draw, making the Supporter naturally held.
3. **Exactly one TM: Evolution and exactly one Jet Energy**
   among those eight visible cards, hence each has one
   copy still unseen.
4. Both unseen spare copies remain in the **searchable deck**
   rather than in the six Prizes.
5. At least one Artazon is in the searchable deck, enabling
   a named Stadium search along either G&H payment mode.

This event contains potential discard candidates, but does not
claim that any two are strategically cheap enough to discard.
The unused Jirachi Ability may be relevant later, but the
event does not model Bench setup, lock threats or end-of-turn
availability. It deliberately excludes G&H acquired through
Tag Call/Stellar Wish, so it is a **narrow natural-route
opportunity census**.

## Exact probability

Let `g` be the number of G&H among the seven visible
non-Jirachi cards and `a` be the number of Artazon among
those cards. Since a searchable Artazon is required,
`a` is zero or one.

The accepted-opening probability is

`A = 1 - C(46,7)/C(60,7)`.

Conditioning on Jirachi occupying one of the initial seven
positions gives the factor `(7/60)/A`.

The remaining seven visible cards are a uniformly selected
subset of the other 59 cards. The number of compatible
selections in category `(g,a)` is

`C(4,g) C(2,1)^2 C(2,a) C(49,7-g-2-a)`.

After those seven are exposed, 52 cards remain unknown.
The unseen TM and Jet must both avoid the six Prizes, and
at least one of the `2-a` unseen Artazon must also
avoid them. The exact Prize-count numerator is

`sum_{j=0}^{1-a} C(2-a,j) C(48+a,6-j)`,

divided by `C(52,6)`.

Summing over `g=1..4` and `a=0..1` yields

`P(event | Basic-valid opener) = 18187043/13418412800`

or **0.135537960197%** of accepted openers, about
**one in 738**.

This is a strict **opportunity upper bound** on benefits that
require precisely this naturally held Jirachi/G&H/TM/Jet/spare
configuration. It is not a bound on alternative lines that
use prior Tag Call, Stellar Wish, later draws, or another
G&H access mechanism.

The most common contribution is `g=1,a=0`, contributing
**0.103762495666%** of accepted openers; less common
configurations account for the remainder.

## Validation and limits

[Exact calculation](../../tools/aichi_held_spare_gnh_opportunity.py);
[independent physical SFT](reproduce.py).

The SFT exhaustively enumerates accepted starting hands, disjoint
Prize sets, and subsequent natural draws in four smaller
labeled-card decks. The category expression matches every one.
It also asserts the exact rational 60-card probability and
recombines all category contributions.

The calculation treats the shuffled sequence by exchangeability:
although the game physically puts Prizes down before the normal
draw, one may first classify the observed opening-plus-draw
positions and then the six unseen Prize positions because those
subsets are disjoint uniformly randomized physical positions.

No opponent effects, setup success, hidden-knowledge optimized
payments, Ticket appearance, or actual match results are evaluated.
Before applying the [52-card thinning theorem](../gnh_large_unseen_information_frontier/),
an analysis must further condition on which Ticket copies are
held, Prized, or searchable, and whether the remaining hand
contains acceptable discard targets.
