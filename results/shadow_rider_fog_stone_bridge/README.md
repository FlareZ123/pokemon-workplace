# Fog Crystal is an indirect Radiant Eternatus search through a Pokémon V Tool host

## Strategic finding

The unchanged [2026 Aichi winning Shadow Rider Calyrex 60-card list](../competitive_deck_baselines/)
has **four Fog Crystal**, **three Shadow Rider Calyrex V**, one Forest
Seal Stone and one Radiant Eternatus. Radiant Eternatus is **Dragon**
type; Fog Crystal searches only for Psychic Energy or a Basic Psychic
Pokémon, so it cannot fetch Radiant directly. Its legal target
Shadow Rider Calyrex V **is a Basic Psychic Pokémon**, and that V can
host the Stone. Stone's Star Alchemy then searches the missing
Radiant directly, or searches a Hisuian Heavy Ball to fetch a Prized
Radiant. This is a concrete indirect source-access path.

| First-turn named source endpoint, conditional on valid opening | Unrestricted other-card discard | Energy-only discard | Energy or spare search Item |
| --- | ---: | ---: | ---: |
| Previous direct, Treasure, Heavy, Quick and Stone routes, including paid T/Q to V host | 53.400320102% | 45.865474298% | 48.132229004% |
| **Additional Fog Crystal V-host branch** | **+1.449240256 pp** | +1.801640909 pp | +1.719278861 pp |
| **Total modeled access** | **54.849560358%** | **47.667115207%** | **49.851507865%** |

The new branch is disjoint from all earlier modeled success sources.
It requires Stone and Fog physically in hand, no eligible V in the
opening/drawn hand, at least one V still searchable in the deck, two
VMAX in deck, and a Radiant access route from Star Alchemy. It is only
counted where no already-paid Treasure/Quick route can produce the
necessary result. For Radiant Prized, Heavy Ball must remain in the
deck. For Radiant in deck, Stone can fetch it directly.

## Exact model

The same full physical 60-card grouping, Basic-valid opening seven,
six hidden Prizes and first natural draw going second are retained.
The opening must contain a non-Radiant Basic that can be Active.
An eligible Shadow Rider V found with Fog enters play before Stone
is attached, then Star Alchemy searches the needed card, the Radiant
enters the Bench from hand and Climactic Gate puts two VMAX directly
from the remaining deck. Initial Bench room, an unused VSTAR Power and
unrestricted Item/Ability channels are assumed.

Implementation:
[tools/shadow_rider_fog_stone_bridge.py](../../tools/shadow_rider_fog_stone_bridge.py).
[Reproducer](reproduce.py).

Of 13 otherwise grouped Basic Pokémon, 3 are Shadow Rider V. Of the
25 generic other cards, one is Stone, four are Fog Crystal and 20
others. Given h grouped Basics in initial hand/draw, p grouped Basics
among Prizes, f generic other cards in initial hand/draw, the joint
physical probability of Stone and Fog held, no V held and at least one
V remaining in deck is exactly:

P = [C(13-h,3)-C(p,3)]/C(13,3) × (f/25)
    × [1-C(20,f-1)/C(24,f-1)].

Each group's allocation across opener, Prize cards and the first
draw is weighted with exact multivariate hypergeometric multiplicities.
The calculation uses reduced Fractions and avoids false independence
between holding Stone and holding Fog within the same 25-card category.

Two independent fully labeled physical 12-card toy universes explicitly
distinguish the V from other Basics and Stone/Fog from other fillers.
Both toy oracles match the exact grouped Fog contribution across all
three payment policies. Actual-card names, print IDs and relevant
Psychic/Dragon types are checked, and exact actual-list rational totals
are pinned by the reproducer.

## Competitive limits

These are **access probabilities for a restricted first-turn action
sequence**, not game or match win rates. Missing: opponent locks,
Tool-slot contention, alternative Fog uses, later Energy/attack value,
other tutors, Supporters and draw abilities, board states and a trained
action policy. The calculation adds the legal Fog chain under an
explicit first-turn endpoint; it does not establish that Fog Crystal
should always search for a V or that any slot swap improves matches.

The strongest next step is to unify all named branches into one
stateful first-turn action policy with competing resources and to
measure subsequent two-turn Underworld Door or attack readiness.
