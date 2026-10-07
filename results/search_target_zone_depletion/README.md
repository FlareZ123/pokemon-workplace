# Search-target zone depletion after setup

## Question

Prize modeling asks whether an important card is trapped in the Prize cards. Deck-search effects create a broader availability question:

**What is the probability that every required search target is still in the deck when the search happens?**

For effects such as Technical Machine: Evolution, a target can leave the searchable zone by entering the opening hand, the Prize cards, or an early draw.

Implementation: `tools/conditioned_searchability.py`  
Independent small-deck validation: `results/search_target_zone_depletion/reproduce.py`

## Why this differs from ordinary Prize risk

Technical Machine: Evolution says to search the deck for a card that evolves from each chosen Benched Pokémon.

A Stage 1 or Stage 2 in hand is therefore unavailable to that particular search. This is especially important on the first turn, where the normal evolution rules prevent simply playing a drawn evolution card. The Advanced Player's Rulebook separately confirms that an effect which puts an Evolution card onto a Pokémon can bypass the ordinary first-turn timing unless its own text forbids doing so.

The relevant state variable is the search zone at the time the effect resolves.

This phenomenon can be called **search-target zone depletion**.

## Exact model

The model has:

- a deck of size `N`;
- `S` forced Basic starters;
- a valid opening hand of size `H`, conditioned on containing at least one forced starter;
- `P` Prize cards;
- `D` ordinary random draws before the search window;
- one or more disjoint non-Basic target groups with specified copy counts;
- a required number of copies that must remain in the deck for each group.

Prize cards and ordinary pre-search draws can be combined into one random exposed block of size `P + D` after the accepted opening because neither selection depends on card identity.

The implementation enumerates the multivariate hypergeometric composition of the accepted opening and then the subsequent exposed block. It sums only states where each target group retains the required number of copies in the deck.

No Monte Carlo sampling is used.

## Aichi timing-window baseline

The 2026 Aichi Vileplume Control list has 14 ordinary Basic starters.

For the first turn going second, use:

- 60-card deck;
- accepted 7-card opening;
- 6 Prize cards;
- 1 ordinary draw before the deck-search attack.

The exact probabilities are:

| Non-Basic target profile | Probability all required groups retain at least one searchable copy |
| --- | ---: |
| singleton `(1)` | 77.162486% |
| two copies `(2)` | 95.094061% |
| three copies `(3)` | 99.015150% |
| four copies `(4)` | 99.816695% |
| two-copy Stage 1 + two-copy Stage 2 `(2, 2)` | 90.371427% |
| two-copy Stage 1 + singleton Stage 2 `(2, 1)` | 73.241397% |
| three-copy + two-copy pair `(3, 2)` | 94.140541% |
| four-copy + singleton pair `(4, 1)` | 77.010511% |
| `(2, 2, 2, 1)` four-channel package | 65.850959% |

The last row is useful for a double Stage 2 line with two copies each of three evolution targets and one singleton target. Before any Basic access, connector access, discard choice, or opponent interaction is considered, there is only a 65.85% chance that all four target categories still have a copy in the deck at this search window.

## Finding 1: singleton search payloads have a hard early ceiling

A singleton non-Basic target is still in the deck only 77.16% of accepted setups at this timing window.

The complement, 22.84%, is the mass where that singleton has already entered the opening hand, Prize cards, or first-turn draw.

For an effect that must search the deck for that card, this is a direct availability ceiling.

## Finding 2: the second copy has unusually large searchability value

Going from one copy to two raises at-least-one-copy searchability from 77.16% to 95.09%, an increase of about 17.93 percentage points.

The third copy raises it to 99.02%. The fourth reaches 99.82%.

This is one reason copy-count decisions for search payloads can have nonlinear value. The first redundancy copy removes most of the early zone-depletion failure mass.

## Finding 3: evolution chains multiply zone requirements

A two-copy Stage 1 and two-copy Stage 2 pair has 90.37% probability of retaining at least one copy of each.

Changing the Stage 2 to a singleton lowers the joint probability to 73.24%.

This explains part of the gap between the Pidgeot and Stoutland endpoints in the Aichi ALS study:

- Pidgeotto and Pidgeot ex are both two-copy search targets;
- Herdier is a two-copy target;
- Stoutland is a singleton.

The Stoutland package begins with a lower search-zone ceiling before its Basic or connector requirements are considered.

## Finding 4: valid-opening conditioning changes the prior slightly

A valid opening is not an unconditional seven-card sample. It is conditioned on containing a Basic starter.

For a non-Basic target, that conditioning slightly changes the chance of being pushed out of the opening hand.

With one singleton target and the same 60-card, 7-hand, 6-Prize, 1-draw timing:

| Forced Basic starters | Singleton remains searchable |
| ---: | ---: |
| 1 | 77.966102% |
| 4 | 77.753837% |
| 8 | 77.492312% |
| 14 | 77.162486% |
| 20 | 76.923467% |
| 30 | 76.720325% |

Low-Basic decks have a stronger accepted-opening conditioning effect because the opening is forced to contain one of a small set of starters. That slightly protects unrelated non-Basic search targets from appearing in the opening.

As the forced-Basic count grows, the conditioning weakens and the singleton probability approaches the unconditional exposure result.

## Finding 5: every pre-search draw consumes singleton searchability

With 14 starters and six Prize cards, the singleton probability changes as ordinary pre-search draws accumulate:

| Draws before search | Singleton remains searchable |
| ---: | ---: |
| 0 | 78.839931% |
| 1 | 77.162486% |
| 2 | 75.485041% |
| 3 | 73.807595% |
| 5 | 70.452705% |

An ordinary draw is beneficial in most card-access models. For a payload that needs to remain in the deck for a search effect, the same draw can move the exact target into the wrong zone.

That creates a state-dependent value reversal. Draw power can increase general access while decreasing the availability of a specific deck-search payload.

## Strategic interpretation

### Searchable is a distinct state from owned

A card in hand is usually considered accessible. A search effect that requires the card to remain in the deck creates a stricter state.

For first-turn evolution effects, the hand can be especially awkward because ordinary evolution timing may prevent using that drawn card directly.

### Copy count should be evaluated against the intended zone

A singleton can be acceptable when any zone is usable and recovery exists.

The same singleton can be fragile when a precise ALS requires it to remain in the deck at a specific time.

### Prize risk is one component of zone risk

Prize-card modeling remains necessary. Search-target modeling adds opening-hand and draw exposure to the same availability question.

A simulator that checks only whether a card is Prized can substantially overestimate a deck-search line.

## Validation

The calculation is exact.

`results/search_target_zone_depletion/reproduce.py` independently enumerates every labeled accepted opening and every disjoint exposed block in a small 10-card test case. The brute-force result matches the category model to floating-point precision.

The reproducer also asserts the reported Aichi profile probabilities.

## Limits

Target groups are assumed to be non-Basic and disjoint from the forced-starter class.

The post-opening Prize and draw block is random. Targeted draw, deck ordering, Prize manipulation, recovery, cards returned to the deck, and search effects before the measured window require an expanded state model.

A card leaving the deck does not always mean the broader game line fails. Some cards can be played from hand, recovered from the discard pile, or returned to the deck. This result measures the narrower condition required by a deck-search effect.

## Relation to ALS modeling

The result supports a stronger ALS representation with explicit zones.

A line should track whether each required piece must be:

- in hand;
- in the deck;
- in the discard pile;
- in play;
- attached;
- Active;
- Benched.

A generic access graph that labels a card merely "available" loses this distinction.

For the Aichi Vileplume list, the distinction is already large enough to change the ceiling on the Stoutland branch.
