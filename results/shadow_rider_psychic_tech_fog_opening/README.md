# Exact initial access to a Psychic Basic counter with Fog Crystal

## Question

For the two complete single-slot [Shadow Rider variants](../decks/shadow-rider-single-psychic-thorns-tech/), how often does the initial seven-card hand contain the chosen singleton Psychic Basic directly or a playable source of it via one existing Fog Crystal, assuming the target has not been Prized?

The one-slot Flutter Mane and Wobbuffet alternatives have the same construction: 60 total cards, **14 Basic Pokémon** including the one-card target, **four Fog Crystal** Items from the champion source, and six initial Prizes.

## Exact constrained model

An initial seven is sampled uniformly; six Prizes are sampled uniformly from the remaining 53 cards. The opener is accepted only if it contains a Basic Pokémon.

Two mutually exclusive events qualify as *hand acquisition access*:

1. The tech is naturally in the initial seven, regardless of the Fog Crystal count.
2. The tech is absent from the initial seven and all six Prizes, at least one **other Basic Pokémon** is in the initial seven to make the opening valid, and at least one Fog Crystal is in that same hand.

The second event assumes Fog Crystal is legally played and used specifically to search the Basic Psychic target from the deck. Fog Crystal's source card text confirms that it searches a Basic Psychic Pokémon or Psychic Energy. Iron Thorns's Initialization does not itself restrict Item use.

Let N=60, B=14 including the tech, F=4 Fog Crystal, H=7 and P=6 Prizes. For numbers b>=1 of other Basics and f>=1 of Fogs in hand:

P(Fog-only event) = sum [C(B-1,b) C(F,f) C(N-B-F,H-b-f)/C(N,H)] × [(N-H-P)/(N-H)].

The direct-tech event has probability H/N, and the valid-Basic-opening probability is 1-C(N-B,H)/C(N,H). Divide the sum of direct and Fog-only events by that denominator for the conditional rate.

## Results

| Exact first-seven event | Conditional on valid seven |
| --- | ---: |
| Target naturally in hand | **13.543697%** |
| Additional non-Prized target found via Fog Crystal held in hand | **29.768008%** |
| **Direct or Fog, disjoint union** | **43.311704%** |

Basic-valid opening seven has probability **86.140932%**.

The exact rational formula is independently checked against exhaustive physically labeled allocations in three small toy decks. The [reproducer](reproduce.py) also verifies that the champion has four Fog Crystal and that both counter Pokémon are eligible Basic Psychic search targets. Implementation: [tools/shadow_rider_psychic_tech_fog_opening.py](../../tools/shadow_rider_psychic_tech_fog_opening.py).

## Strategic interpretation and limitations

This 43.31% is a **static search-source availability endpoint**, not the probability that the tech reaches the Active Spot in time, nor an estimate of winning games against Iron Thorns. It deliberately omits the first natural turn draw, possible starting Active choice, more flexible Mysterious Treasure or Quick Ball search routes, Hisuian Heavy Ball recovery, manual Bench placement restrictions, actual plays that get the tech Active, and the opponent's actions.

Most importantly, four Fog Crystals are already valuable connectors in Shadow Rider. Using one to find Flutter Mane or Wobbuffet excludes an alternative use that might have found an attacking Basic or Psychic Energy; four nominal access cards do not provide four free opportunities. A tech searched to hand after setup cannot retroactively be the initial Active, whereas one naturally in the seven could have been selected Active.

At the source-lock layer, [Flutter and Wobbuffet differ](../wobbuffet_flutter_thorns_continuation/): Flutter allows Dragon Radiant Eternatus's Climactic Gate while suppressing Thorns; Wobbuffet prevents it while Active. Thus identical search-source probabilities conceal different legal turn continuations.

The related [Dream Ball/Alolan Muk opening allocation](../dream_ball_muk_opening_allocation/) reports much smaller conditional first-Prize percentages, but it measures a different event with a different action and timing. Those percentages must not be subtracted or treated as a validated comparative win forecast.

Next work should add source contention, target placement, pivot timing, and actual game-policy outcomes before recommending either counter over the champion list.
