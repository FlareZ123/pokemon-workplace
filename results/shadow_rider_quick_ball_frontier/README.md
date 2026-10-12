# Aichi Shadow Rider: the missing Quick Ball Radiant launch branch

## Finding

The actual 2026 Aichi Open League champion list already includes one
Quick Ball. Its Basic-Pokémon search can obtain the singleton Dragon-type
Radiant Eternatus from the deck, after discarding another card from hand.
Earlier exact Radiant launch studies deliberately excluded this legal
connector. The source-constrained first-turn opening envelope increases
from **44.937944013%** (direct hand, Mysterious Treasure, Hisuian Heavy Ball)
to **50.659437625%**, a **5.721493612-percentage-point** addition from
Quick Ball in worlds lacking those other routes.

This is a bounded **access event**, not an observed match win rate.

## Real exact-print deck and action contract

The full [60-card Aichi winning baseline](../competitive_deck_baselines/)
remains unchanged: Radiant Eternatus ×1, Shadow Rider Calyrex VMAX ×4,
Mysterious Treasure ×4, Hisuian Heavy Ball ×1, Quick Ball ×1,
13 other Basic starters, 11 Psychic Energy, 25 remaining cards.

Source print IDs are swsh12pt5-105, swsh6-75, sm6-113, swsh10-146,
and swsh1-179, respectively. The reproducer validates all source card
texts and the full paper Expanded baseline legality proof.

The calculation conditions on a Basic-valid seven-card opening, chooses
a non-Radiant Basic as the opening Active, sets six physical face-down
Prizes, and takes one natural draw going second. To launch, a Radiant
must reach the hand and enter the Bench from hand, and at least two Shadow
Rider VMAX must still be in the deck for Climactic Gate. Opening Active
selection occurs before the first draw.

Only one named search Item is used to access Radiant. Mutually exclusive
routing priority is: directly held Radiant; Heavy Ball if Radiant is
Prized; Mysterious Treasure if Radiant is in deck; Quick Ball if Radiant
is in deck and Treasure was not already accessible. Quick Ball and
Mysterious Treasure each consume a different hand card as payment. There
are six or more other hand cards after reserving the opening Active, so
mechanical payment is always possible under the unrestricted policy.

## Exact results

| Mutually exclusive route | Probability of an accepted opener |
| --- | ---: |
| Radiant already in hand | 12.017840120% |
| Heavy Ball retrieves Prized Radiant | 1.238781582% |
| Mysterious Treasure fetches Radiant (unrestricted discard) | 31.681322310% |
| **Quick Ball fetches Radiant only when these are unavailable** | **5.721493612%** |
| **Total named source envelope** | **50.659437625%** |

A discard-preservation test separates actual mechanic feasibility from
hypothetical choice constraints:

| Hypothetical acceptable one-card payment | Total dual-VMAX launch |
| --- | ---: |
| Any other held card | **50.659437625%** |
| Held Psychic Energy only | **42.703458196%** |
| Held Psychic Energy or an extra held search Item (spare Treasure or Quick Ball) | **45.066291589%** |

In the Energy-only case, Quick Ball adds **4.602864405 percentage
points** to the earlier direct/Heavy/Treasure Energy-paid baseline of
**38.100593791%**. Treating Psychic Energy as an acceptable discard is
a defined sensitivity case, not a recommended real-game policy; Underworld
Door may need Energy in hand.

## Method and verification

- Implementation: [tools/shadow_rider_quick_ball_frontier.py](../../tools/shadow_rider_quick_ball_frontier.py).
- Reproducer: [reproduce.py](reproduce.py).
- Exact grouped multivariate-hypergeometric opener, Prize allocation and
  first-draw counts use Python integers and reduced Fractions. Every
  accepted world's probability mass is accounted for.
- Two **independent labeled physical-card** small-deck oracles, with
  distinct search-copy configurations, enumerate the actual physical
  opening, Prize and draw cards. Their complete route partitions match
  the category enumerator exactly.
- Source-grounded first-turn direct/Heavy/Treasure fractions reproduce
  the independently established previous results, and removing the one
  Quick Ball restores the previous 44.937944013% ceiling.

## Limitations and strategic implications

No additional draw engines, Fog Crystal (Radiant is Dragon rather than
Psychic), Forest Seal Stone, VS Seeker, item locks, opponent interference,
Bench crowding, alternative Basic searches, card-specific discard DCI, or
post-launch turns are modeled. Search priority is chosen for this single
Radiant/two-VMAX endpoint; it is not globally optimal action sequencing.
Future comparison should integrate the actual Forest Seal Stone and Quick
Ball competing uses, initial V availability, bench capacity, and later
Underworld Door/attack timelines before recommending deck modifications.
