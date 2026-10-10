# Which TAG TEAM Supporters can an early Tag Call actually find?

## Question

An already-held Tag Call may search for up to two TAG TEAM cards
from the deck. The Aichi runner-up Vileplume list includes both
Guzma & Hala (G&H) and Bellelba & Brycen-Man as TAG TEAM Supporters.

Previous work, [aichi_tagcall_bellelba_ceiling](../aichi_tagcall_bellelba_ceiling/),
identified a rare case where a single Bellelba is the only searchable
TAG TEAM Supporter. Here we classify **all** physical target-existence
possibilities after the accepted opener, normal draw and Prize cards.

Implementation: tools/aichi_tagcall_target_availability.py.
Reproducer: [reproduce.py](reproduce.py).

## Population and event

Published Aichi runner-up list counts from tools/aichi_setup_inference.py:

- 60 cards, 14 eligible Basic Pokémon, including one Jirachi;
- four G&H TAG TEAM Supporters;
- four Tag Call Items;
- one Bellelba & Brycen-Man TAG TEAM Supporter.

Condition on a Basic-valid seven-card opening, place six hidden Prizes,
and add the first normal turn draw.

Study the **natural Jirachi/G&H/Tag Call triplet** event: Jirachi must
be in the opening seven; at least one G&H and one Tag Call must be
visible by the next draw (which can be in either the opening or turn
draw). No search, discard or other gameplay action has occurred yet.

The partition is based on the number of unprized, not-visible physical
G&H and Bellelba copies remaining in the deck. It excludes any
current hand copies from the Tag Call target count.

## Exact partition

All percentages in the second column use **all Basic-valid accepted
openings** as denominator. The third column conditions further on
the natural Jirachi/G&H/Tag Call triplet.

| Additional G&H searchable? | Bellelba searchable? | All accepted starts | Among triplet starts |
| --- | --- | ---: | ---: |
| No | No | 0.000975797366% | 0.048129230437% |
| No | Yes | **0.005531280123%** | **0.272819198998%** |
| Yes | No | 0.398434091445% | 19.651955292154% |
| Yes | Yes | 1.622511496828% | 80.027096278411% |
| **Total natural triplet** | | **2.027452665762%** | **100%** |

Exact triplet probability:

\[
\Pr(J \text{ in opener},\ G\ge1,\ T\ge1\mid
\text{Basic-valid}) =
\frac{14895153}{734673280}.
\]

The previously isolated Bellelba-only cell exactly reproduces
**74221/1341841280**.

**Consequence:** the G&H-only supplemental Tag Call target model has
another searchable G&H in about **99.68%** of the natural triplet
positions, while Bellelba offers the only TAG TEAM Supporter target in
about **0.273%** of these positions. The natural triplet itself is
only about **2.027%** of accepted starts.

This says G&H presence is common under this conditioning. It does
not mean the best line always searches G&H. Bellelba's future strategic
value, discardability and the cost of other connectors can make the
identity of the searched Supporter matter even when both are available.

## Combinatorial method

Fix Jirachi in the initial seven (unconditional probability 7/60).
There are then seven visible non-Jirachi cards after one natural draw,
from the other 59 cards. For each visible multiplicity

- k = G&H copies held, from 1 to 4;
- t = Tag Call copies held, from 1 to 4;
- b = Bellelba copies held, either 0 or 1,

the exact visible sample weight is

\[
w_{k,t,b}=
\frac{\binom{4}{k}\binom{4}{t}
\binom{1}{b}\binom{50}{7-k-t-b}}
{\binom{59}{7}}.
\]

The remaining 52 unseen cards contain 4-k G&H, 1-b Bellelba
and the untyped residual stock. Enumerate g and v, the number of
G&H and Bellelba copies among six hidden Prizes. Their joint
conditional weight is multivariate hypergeometric:

\[
\frac{\binom{4-k}{g}\binom{1-b}{v}
\binom{47+k+b}{6-g-v}}{\binom{52}{6}}.
\]

G&H remains searchable iff 4-k-g > 0; Bellelba remains searchable
iff 1-b-v > 0. Sum the weighted states in each cell; multiply by
7/60 and divide by

\[
\Pr(\text{Basic-valid})=
1-\frac{\binom{46}{7}}{\binom{60}{7}}
=\frac{252032}{292581}.
\]

The calculation rearranges turn draw before Prize placement only
within the exchangeable unknown-card population, preserving the
actual physical joint distribution.

## Validation

The tests independently enumerate a physically labeled 11-card deck:
one Jirachi, two other Basics, two G&H, two Tag Call, one Bellelba and
three fillers. They enumerate all accepted initial four-card hands,
one natural draw and two hidden Prizes, then inspect the remaining
physical deck rather than using the formula.

The exact 11-card partition is:

- Neither: 7/195;
- Bellelba only: 62/1365;
- G&H only: 4/65;
- Both: 4/91.

Total natural triplet probability is **17/91**.
The 60-card result reproduces the previously independent
Bellelba-only exact fraction.

Validation: [GitHub Actions run 38061349765, passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38061349765).

## Scope and next step

The partition measures **searchable deck cards** under a constrained
natural opening event. It does not simulate Tag Call's execution,
actual G&H payment, secondary Bellelba value, Jirachi's Stellar Wish
or terminal setup; it also assumes the first meaningful card action
has not removed relevant cards.

A useful next step is to repeat the action-set ablation in
[results/aichi_tagcall_information_preview](../aichi_tagcall_information_preview/)
with Bellelba as an explicitly selectable extra target, preserving
which Supporter was searched, what was discarded, and the original K0
decision boundary. This can determine whether searching Bellelba
adds any attainable wins in the model.
