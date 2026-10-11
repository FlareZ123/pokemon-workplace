# Exact natural-route Aichi Ticket thinning: tiny accepted-start ceiling

## Motivation

The 2026 Aichi Vileplume solver omitted a legal Guzma & Hala
two-card payment when TM: Evolution and Jet Energy are already
held. The [physical counterexample](../gnh_optional_paid_duplicate_search/)
proves the optional payment can still search extra Tool and
Special Energy cards; the [52-card theorem](../gnh_large_unseen_information_frontier/)
calculates its abstract mean deck-thinning effect.

The key practical question is more restrictive: **how much direct
first-window Ticket access can this extra search add across
accepted openings where all of the required natural named cards
are actually in the right places?**

## Exact event

Start from the published 60-card Aichi composition, including
14 Basics, singleton Jirachi, four G&H, two TM: Evolution, two
Jet Energy, and two Artazon. Replace one otherwise
first-turn-neutral non-Basic TechSlot with one hypothetical
Ticket-role Item, preserving all source-card counts of interest.

As in the [natural held-spare census](../aichi_held_spare_gnh_opportunity/),
require Jirachi in the starting seven, a naturally held G&H
after one turn-start draw, exactly one held TM and Jet, both
spares in the searchable deck, and at least one searchable
Artazon. **Additionally require the Ticket to be in the deck
after all six Prizes and the natural draw.**

This joint event occurs in exactly

`4777859/4341251200 = 0.110057188121%`

of Basic-valid accepted starts. Among the broader
`0.135537960197%` named-resource event, the Ticket is
searchable in exactly `7062922/8698151 ≈ 81.200269%`
of cases.

The calculation enumerates visible G&H/Artazon counts and
all remaining Prize subsets by exact integer combinatorics,
excluding spare TM, spare Jet and Ticket from Prizes while
requiring at least one Artazon unprized.

## First unused Stellar Wish increment

After seven opening cards, one draw and six Prizes,
the initially searchable deck contains **46 cards**.
Assume the two-card payment is strategically harmless,
that the player can execute G&H normally, and that
Jirachi remains Active with an unused, legal Stellar Wish
to inspect five shuffled cards.

The conventional no-payment G&H line retrieves an
Artazon, leaving 45 cards. The paid duplicate-search line
also retrieves the spare TM and spare Jet, leaving 43.

Since the Ticket is known to be in the searchable deck
in the joint event:

| Line | Ticket in late five-card Wish |
| --- | ---: |
| Artazon only | `5/45 = 11.111111%` |
| Artazon, spare TM, spare Jet | `5/43 = 11.627907%` |
| **Conditional direct hit improvement** | **`2/387 = +0.516795866 pp`** |

Averaging the benefit only over eligible accepted starts gives

`(4777859/4341251200) * (2/387)`

`= 111113/19535630400`,

or **+0.000568770998 percentage points of accepted
opening probability**.

This is an **optimistic upper bound on this particular
immediate Ticket top-five thinning channel** for naturally
held Jirachi/G&H/TM/Jet. In many of the eligible states,
the two payment cards could be valuable, the late Wish
could be unavailable, or a prior alternative line might
already access Ticket. Such complications can reduce or
erase the real incremental advantage.

The bound does not cover other benefits of acquiring spare
Tool/Energy, alternative G&H access through Tag Call or early
Stellar Wish, later setup turns, multi-target Item packages,
or match-winning effects. It should not be interpreted as
a global upper bound on G&H or deck optimization.

## Why this differs from the 52-card mean theorem

The unconditional `5/51 -> 5/49` formula averages over
many Prize configurations, including worlds where a named
source is unavailable. This result **conditions on all
three fetches actually being accessible** and on the
Ticket being in the deck, so the postsearch sizes
are deterministically 45 and 43. Applying the general
unconditional 52-card difference inside this selected
event would misweight the sample.

This is precisely why access geometry, Prize conditioning,
and actual observation timing must be evaluated jointly.

## Verification

Calculation:
[tools/aichi_held_spare_ticket_lift.py](../../tools/aichi_held_spare_ticket_lift.py).
Independent physical SFT: [reproduce.py](reproduce.py).

The regression exhaustively enumerates accepted opening
hands, disjoint hidden Prize sets, and a subsequent natural
draw across four smaller labeled decks. It checks exact
joint named-resource/Ticket probability against the
category count, then asserts the full 60-card rational
mass and final bound.

No opponent behavior, K0 information-optimal cost policy,
TechSlot's overall strategic opportunity cost, or realistic
game win-rate is modeled. The original Aichi roster does
not literally include Ticket; it is a hypothetical Item
assignment used by the existing Ticket package research.
