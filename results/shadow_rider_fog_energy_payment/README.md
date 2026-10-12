# Fog Crystal can supply a discard payment for the Radiant launch

## Finding

The unchanged 2026 Aichi champion list contains four Fog Crystal,
four Mysterious Treasure, one Quick Ball and eleven Basic Psychic
Energy cards. Fog Crystal can search for a Psychic Energy card.
When a held Treasure or Quick Ball has no Psychic Energy naturally
available in hand, a Fog Crystal **can fetch an Energy from deck**
which can then be discarded to pay that Item and search the singleton
Dragon-type Radiant Eternatus. This two-Item source is mechanically
distinct from a naturally held Energy payment.

This result adds new worlds to the
[Quick Ball + Stone + host-search + Fog-host launch frontier](../shadow_rider_fog_stone_bridge/),
excluding overlap with its already-available Stone and Fog routes.

| First-turn paid-search resource discipline | Access before Fog-funded payment | Additional Fog -> Energy -> Treasure/Quick | New source-access union |
| --- | ---: | ---: | ---: |
| Arbitrary legal other-card discard | 54.849560358% | +0.000000000 pp | 54.849560358% |
| Psychic Energy naturally held | 47.667115207% | **+3.385921756 pp** | **51.053036964%** |
| Natural Energy or held spare search Item | 49.851507865% | **+2.465480483 pp** | **52.316988349%** |

In the last two rows, the new total **allows a supplemental Fog
Crystal action to supply Psychic Energy before the paid Item**.
This differs from the original "naturally held" conservation policy:
an Energy from the deck can now be used as a discard payment, provided
Fog Crystal itself is held and a Psychic Energy remains in deck.

## Exact account of overlapping routes

We condition on a Basic-valid opening seven, six physical face-down
Prizes and one first-turn draw going second; a non-Radiant Basic was
available as opening Active and at least two Shadow Rider VMAX remain
in the searchable deck.

The new branch requires Radiant in deck, held Treasure or Quick,
zero Psychic Energy in the hand, a Psychic Energy in deck and an
available Fog Crystal in hand. Other permitted paying sources are
considered before the Fog action; success is credited only if those
earlier sources cannot pay.

Some hands also have Forest Seal Stone with an available Shadow Rider V,
or have a Stone and Fog that can fetch a deck V to host Stone. Such hands
were already successful in earlier parts of the frontier. They must be
subtracted to avoid double-counting.

From the grouped 25 filler cards (one Stone, four Fog and 20 others),
for f held fillers the exact chance of at least one held Fog is

F = 1 - C(21,f)/C(25,f).

The chance of both Stone and Fog held is

SF = (f/25) × [1 - C(20,f-1)/C(24,f-1)].

Three V cards among thirteen other Basics are available in hand or deck
unless all three are Prized; if p of those Basics are in Prizes, that
probability is 1 - C(p,3)/C(13,3). Therefore the new access fraction
conditional on this category state is

F - SF × [1 - C(p,3)/C(13,3)].

This nonindependence-aware formula is integrated against exact
opening/Prize/draw multiplicities with reduced Fractions.

## Reproducibility

Implementation:
[tools/shadow_rider_fog_energy_payment.py](../../tools/shadow_rider_fog_energy_payment.py).
[Reproducer](reproduce.py).

Two independent toy-deck physical enumerations explicitly label
one Stone, one Fog, a V and individual Psychic Energy instances.
The physical worlds test Fog availability, remaining Energy in deck,
the natural-payment gate and whether Stone/Fog would already have
rescued the same world. Both agree exactly with the grouped calculation
for all three payment modes. The reproducible actual-list fractions
are pinned and the full published 60-card baseline is legality-checked.

## Limits

This is a narrow setup-access calculation, **not a match win-rate
measurement**. It assumes usable Item actions and that choosing to
discard the fetched Psychic Energy is acceptable. Actual play may value
that Energy, Fog Crystal or the other Item differently. Other search
routes, alternate payment cards, Item locks, opponent interference,
turn-by-turn Energy acceleration, attacks and match outcomes are outside
the model. The cumulative totals are a source-access envelope under
the explicitly expanded action vocabulary.
