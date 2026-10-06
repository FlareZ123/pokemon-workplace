# Clean direct outs for first Prize-rescue access

## Question

How should a timed Prize-rescue model credit deterministic non-Supporter search cards that can find Gladion in the current Supporter window?

Treating each search card as another Gladion copy is structurally wrong. A search out only works if it is seen and at least one real, unprized Gladion remains in the searchable deck.

This result adds an exact setup-conditioned model for that distinction.

Implementation: tools/direct_rescue_outs.py

Reproducer and exhaustive validation: results/direct_rescue_outs/reproduce.py

## Abstract card class

The model introduces a deliberately idealized **clean direct out**.

A clean direct out is a non-starter card that is already assumed to be playable before the current Supporter window and, when seen, can search one Gladion-like rescue Supporter from the deck into the hand.

This abstraction does not claim that Computer Search, Secret Box, Call Bell, Xtransceiver, or any other concrete card is universally clean. Their real discard costs, timing restrictions, coin flips, ACE SPEC contention, lock sensitivity, and connector opportunity costs must be handled separately.

The abstraction answers a narrower question:

> If a deck really does have O deterministic same-window outs under the current state, how much do they improve first-rescue access?

## Exact setup order

The model follows literal setup order.

1. A seven-card opening hand is accepted only if it contains a setup-eligible starter.
2. Six Prize cards are selected from the remaining deck.
3. Additional non-Prize cards are exposed until a configured cumulative cards-seen count is reached.
4. The state is conditioned on at least one modeled critical singleton being Prized.
5. The model asks whether at least one Gladion can be played from hand in the current Supporter window.

All modeled critical cards, Gladion copies, and direct outs are non-starters in this first version.

## Access condition

First-rescue access succeeds if either:

- at least one Gladion copy has been exposed into the hand; or
- at least one clean direct out has been exposed and at least one Gladion remains in the searchable deck.

The second condition is the key distinction from copy counting.

If every real Gladion is in the Prize cards, an Item that normally searches Gladion is not a Gladion.

## Validation

The reproducer exhaustively enumerates every labeled permutation of a small eight-card deck, applies valid-opening conditioning, takes the next cards as Prizes, exposes the later cards in order, and evaluates the access condition directly.

The exact combinatorial result matches the exhaustive permutation frequency to floating-point precision.

The same reproducer also checks that the marginal probability of a critical non-starter being Prized matches the established valid-start-conditioned Prize model.

## Main baseline

Use:

- 60-card deck;
- 6 Prize cards;
- 7-card accepted opening hand;
- 12 setup-eligible starters;
- 4 critical non-starter singletons;
- 2 non-starter Gladion-like rescuers;
- condition on at least one critical being Prized.

The exact probability that at least one modeled critical is Prized after valid-start conditioning is **35.383108%**.

### Eight random non-Prize cards seen

With eight cumulative random non-Prize cards exposed into hand before the modeled Supporter window:

| Clean direct outs | P(first rescue access | a critical is Prized) |
| ---: | ---: |
| 0 | 24.265475% |
| 1 | 34.282592% |
| 2 | 43.128752% |
| 3 | 50.920673% |
| 4 | 57.765545% |
| 5 | 63.761624% |
| 6 | 68.998807% |
| 7 | 73.559177% |
| 8 | 77.517529% |

The first few clean outs produce large gains because the baseline has only two Gladion copies and sparse exposure.

These are state-conditional mathematical values. They are not recommendations to add eight search cards to a deck.

## Exposure sensitivity

| Cards seen | 0 outs | 2 outs | 4 outs | 6 outs | 8 outs |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 21.2442% | 38.4351% | 52.3388% | 63.4808% | 72.3207% |
| 8 | 24.2655% | 43.1288% | 57.7655% | 68.9988% | 77.5175% |
| 10 | 30.1307% | 51.6987% | 67.0664% | 77.8557% | 85.3099% |
| 12 | 35.7596% | 59.2514% | 74.5674% | 84.3663% | 90.5077% |
| 16 | 46.3085% | 71.6363% | 85.2930% | 92.4511% | 96.0884% |

Random exposure and targeted access are distinct axes. The model can increase either without pretending they are the same mechanic.

## Search outs are weaker than extra Gladion copies

A common simplification is to count each deterministic search out as an extra copy of its target.

That slightly overstates access even in this favorable clean-out model.

At eight cards seen:

| Clean outs | Correct access | Naive model treating each out as an extra Gladion | Overstatement |
| ---: | ---: | ---: | ---: |
| 1 | 34.282592% | 34.365853% | 0.083261 percentage points |
| 2 | 43.128752% | 43.285531% | 0.156779 percentage points |
| 4 | 57.765545% | 58.043943% | 0.278397 percentage points |
| 8 | 77.517529% | 77.959975% | 0.442446 percentage points |

The gap occurs when an out is exposed while every real Gladion is unavailable to search, especially when the actual Gladion copies are Prized.

The numerical gap is modest in this baseline. The representational point is broader: an access connector and its target are different resources with different failure modes.

## Relation to the previous timed model

results/prize_rescue_deadline measures whether enough actual rescue copies arrive across multiple Supporter windows to recover all initially Prized critical cards.

This result answers a different intermediate question: can the player access at least one rescue copy in the current modeled window when deterministic search outs are present?

The models should eventually be combined. A clean direct out can create a targeted Gladion arrival before a window. It should not be inserted as another physical Gladion in Prize topology, and it should not be represented by simply increasing random cards_seen.

## Strategic interpretation

This result formalizes another part of connector realism.

An optimizer should distinguish at least:

- target copies;
- deterministic direct outs;
- stochastic outs;
- multi-card connector chains;
- Supporter-consuming outs;
- attack-consuming outs;
- zone-specific routes;
- costs and lock sensitivity.

A direct out can sharply improve early access while leaving topology unchanged.

A concrete card can also cease to be a clean out in a real state. Secret Box may lack three acceptable discards. Call Bell may be outside its first-turn-going-second window. Computer Search may lose the ACE SPEC slot to another card. Xtransceiver can fail its coin flip.

Therefore, the table is best read as an upper-layer combinatorial primitive for cards whose state-specific AMR has already been established.

## Limitations

The model includes only non-starter criticals, rescuers, and outs.

It does not yet model:

- direct outs that are themselves setup starters;
- Tapu Lele-GX-style two-step Pokémon connector routes;
- stochastic search;
- discard-pile access such as Battle Compressor plus VS Seeker;
- multiple rescue plays across later Supporter windows;
- Supporter contention;
- concrete lock states;
- connector costs;
- ordinary Prize-taking;
- deck-specific target competition.

The exact model can still serve as a reusable baseline for future typed-access work.

## Next useful work

The next useful integration is to let the typed access network emit targeted-access events into the multi-window Prize-rescue model.

A first combined experiment could compare four packages with the same physical Gladion count:

1. random exposure only;
2. clean direct Items;
3. a Tapu Lele-GX route requiring a Basic-search Item and an open Bench;
4. Battle Compressor plus VS Seeker.

The goal should be to quantify access while preserving each route's topology, timing, and state requirements.
