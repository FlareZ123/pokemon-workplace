# A second TAG TEAM name can fill Tag Call's unused search slot

## Mechanistic question

Tag Call searches for up to **two** TAG TEAM cards. The original
first-turn Aichi preparer modeled its supplemental copy as searching
additional Guzma & Hala (G&H) copies, which can be discarded to pay
G&H's optional two-card cost.

The same Aichi list runs singleton Bellelba & Brycen-Man, another
TAG TEAM Supporter. When exactly one G&H remains searchable, Tag Call
can obtain **both G&H and Bellelba** in a single Item search. The
extra physical card changes the possible payment stock even though
the deck always uses only one Supporter per turn.

We quantify this missing **second-output material opportunity**
without assuming Bellelba is strategically disposable.

## Model

Use the Aichi 60-card deck composition, 14 Basic starters including
singleton Jirachi, four G&H, four Tag Call, and one Bellelba.

Condition on a Basic-valid seven-card opener, Jirachi in the initial
seven, at least one G&H and Tag Call in the seven non-Jirachi visible
cards after one natural draw, and six hidden Prizes. This is the same
natural triplet event as in
[aichi_tagcall_target_availability](../aichi_tagcall_target_availability/),
whose total mass is 2.027452665762% of accepted starts.

Let g be the number of extra G&H cards still in the searchable deck,
and b be the Bellelba singleton's searchable count, either zero or
one.

- The G&H-only Tag Call model obtains up to min(2,g) physical cards.
- The expanded, card-text-permitted model can obtain up to
  min(2,g+b) physical cards.
- An additional card exists precisely when b=1 and g is 0 or 1.
- That additional card **completes a two-card output** precisely
  when b=1 and g=1.

G&H has already been reserved as the Supporter for the turn and
removed from the modeled hand; all named fetched copies remain
separate physical resources. This is a search-output bound rather
than an assertion that Bellelba should be discarded.

## Exact physical-card availability

| Searchable extra G&H | Bellelba searchable? | Accepted-start frequency | Among natural triplet |
| ---: | --- | ---: | ---: |
| 0 | Yes | 0.005531280123% | 0.272819199% |
| **1** | **Yes** | **0.102471870248%** | **5.054217639%** |
| 0 or 1 | Yes | **0.108003150371%** | **5.327036838%** |

The exact second-card completion event is

\[
\Pr(g=1,b=1\mid\mathrm{accepted})=
\frac{66550477}{64945117952}.
\]

The exact broader opportunity to fetch one additional card is

\[
\Pr(g\le1,b=1\mid\mathrm{accepted})=
\frac{350713867}{324725589760}.
\]

Thus the overlooked extra-copy case (g=1) is about **18.53
times** as frequent as the previously investigated Bellelba-only
fallback (g=0) in this particular opening model. Of the 2.02745%
natural Jirachi/G&H/Tag Call openings, about **5.05%** can physically
get a second search output by including Bellelba.

If Bellelba is UDP because it serves an important control plan, its
value as discard fuel can be much lower. Fetching it may still remove
one irrelevant-to-this-objective card from the deck and change future
draw/search density, but the latter is a different effect.

## Validation

Extends the exact integer-weight hidden-Prize enumeration at
tools/aichi_tagcall_target_availability.py with physically searchable
G&H copy counts 0..3 and Bellelba count 0..1.

The independent 11-card physical oracle enumerates every accepted
four-card opening, next draw and disjoint two-Prize subset and
classifies literal remaining copies. It reproduces the full count
partition; in that toy case the extra-Bellelba-stock event equals
**122/1365**.

The 60-card regression asserts the exact fractions above and that
all detailed category weights partition the natural triplet mass.
[GitHub Actions validation](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-aichi-tagcall-second-slot.yml).

## Limitations

The occurrence of a second physical TAG TEAM search output is a
necessary precondition for certain new payment lines, not sufficient
for reaching a terminal Vileplume setup or improving game outcomes.
The search may be strategically undesirable if a valuable singleton
is consumed, and the model omits other ways to obtain discard stock.

A follow-up simulator at tools/aichi_tagcall_bellelba_payload.py
extends the existing Aichi named-card payment model and measures
whether the extra Bellelba can change a downstream first-reset
access endpoint. That experiment requires separate output and
interpretation.
