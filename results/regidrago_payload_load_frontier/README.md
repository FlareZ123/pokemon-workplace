# Regidrago: exact Dragapult discard loading versus second-copy swaps

## Why physical access is insufficient

The [2026 Aichi 10th-place Regidrago reference](../competitive_deck_baselines/) uses one Dragapult ex Stage 2 as the Phantom Dive source, one Battle Compressor, three Quick Ball, three Mysterious Treasure, and four Regidrago V. The prior [initial Prize coverage result](../regidrago_payload_prize_coverage/) established that replacing some non-Basic card with a second Dragapult ex improves initial non-Prize payload inventory. **Apex Dragon copies only Dragon Pokémon attacks in the discard pile.** An accessible Dragapult still has to reach that zone. This study measures exact opening Item routes, including competition between a second source copy and the very Item that loads it.

Bundled print text was checked: Battle Compressor (`xy4-92`) discards up to three selected deck cards; Mysterious Treasure (`sm6-113`) discards one hand card and searches for a Psychic or Dragon Pokémon; Quick Ball (`swsh1-179`) discards one other hand card and searches for a Basic. Dragapult ex (`sv6-130`) is Dragon Stage 2; Regidrago V (`swsh12-135`) is Dragon Basic.

## Explicitly limited turn-one action language

Uniform shuffle, **7-card Basic-valid opening**, 6 initial face-down Prizes, then one natural draw. Basic starters comprise four Regidrago V and eleven other Basics in all candidate decks. We test whether Dragapult can be physically placed into discard using any of:

1. **Battle Compressor:** Compressor is in the first eight seen cards, and at least one Dragapult is still in the deck.
2. **Held-source payment:** at least one Dragapult is in the first eight and a Quick Ball or Mysterious Treasure is held, with at least one Regidrago V still searchable in the deck.
3. **Two-Item chain:** Mysterious Treasure can fetch a deck-resident Dragapult; a second Quick Ball or Mysterious Treasure can discard the fetched card, with a Regidrago V still searchable. The first Treasure also needs one payment card.

The **direct** metric permits only routes 1 and 2. The **ideal** metric also permits route 3 with any remaining card serving as the first Treasure payment. The **safe-D** metric permits route 3 only if at least one of D explicitly designated disposable filler cards is in the visible eight. This DCI-like protection is an **exogenous scenario**, not a judgment that all other cards can be safely burned. Discarding Dragapult itself via the second Item is always purposeful.

Other effects, draw Supporters, Tapu Lele, Dedenne, Squawkabilly, earlier deck searches, normal prize taking, attacks, Bench choices, and opponent locks are excluded. Only Regidrago V is accepted as a sufficient deterministic Quick Ball/Treasure search target. Other real eligible targets may improve legal payment access. Thus the model measures the named routes under these deliberate restrictions; it is neither full first-turn attack setup nor a global attainable ceiling.

## Exact results (one natural draw, 15 Basics, 60-card candidates)

| Second Dragapult replaces | Direct named routes | Direct change | Ideal with any first Treasure payment | Safe-D with D=20 |
| --- | ---: | ---: | ---: | ---: |
| No swap, published list | **16.845955%** | baseline | 26.556524% | 25.982046% |
| Unspecified non-Basic filler | 24.042923% | **+7.196967 pp** | 33.763553% | 33.232644% |
| One Quick Ball (3 to 2) | 22.576011% | +5.730056 pp | 30.283151% | 29.846409% |
| One Mysterious Treasure (3 to 2) | 22.576011% | +5.730056 pp | 28.688820% | 28.337344% |
| Battle Compressor (1 to 0) | **12.873922%** | **-3.972033 pp** | 23.727473% | 23.085348% |

The published singleton is outside Prizes at all in **89.941382%** of accepted starts; a second Dragapult raises the corresponding **inventory** coverage to **99.142625%** in each replacement variant. Yet cutting Battle Compressor reduces even the narrow direct discard-routing frequency. This is a concrete counterexample to optimizing Prize redundancy without modeling the connector lost to the swap.

The direct-route result does not depend on the assumed disposable filler count. Two-Item chains are sensitive to discardability. With no designated safe filler, safe-D collapses to the direct result. At D=10, 20, 30, safe-D for the published list is **23.704527%**, **25.982046%**, **26.497842%**; for the second Dragapult at the cost of Compressor it is **20.539736%**, **23.085348%**, **23.661876%**. The safe-D ranking can differ from the idealized unlimited-discard ranking.

## Method and verification

`tools/regidrago_payload_load_frontier.py` enumerates all multivariate-hypergeometric eight-card visible hand category counts with an **exact** correction for the first seven containing a Basic: among eight visible cards with exactly one Basic, seven of the eight possible natural-draw positions correspond to accepted openings. Prize composition for Dragapult and Regidrago V is then enumerated exactly; the rest of the deck can be combined combinatorially because the policy never searches a different named target. All reported probabilities use integer arithmetic and Python `Fraction`.

`results/regidrago_payload_load_frontier/reproduce.py` is a wholly independent **labeled physical-card oracle** for four twelve-card toy decks, dealing the accepted opener, disjoint Prizes, and next draw directly. All eleven event metrics match the category solver exactly in every toy deck. Structural tests check that direct is no larger than safe-D, safe-D no larger than ideal, and ideal no larger than unprized inventory across all five candidates and four D settings. Windows CI runs this single-file regression.

## Strategic interpretation

A second Dragapult ex is promising on paper if Phantom Dive availability is a bottleneck, but its value depends on the **specific outgoing card** and the probability of loading the source into discard before Apex Dragon is needed. Removing the sole Battle Compressor damages the measured direct-loading line even while strengthening Prize redundancy. Cutting a search Item also reduces the benefit. This suggests preserving Compressor when testing a second Dragapult, subject to proving that an alternative Trainer slot can be removed without hurting earlier attacker setup, matchups, lock counterplay, or action sequencing.

Next experiment: select the actual outgoing card for a legal named 60-card variant, introduce the time required to establish Regidrago VSTAR and its Energy, and evaluate Phantom Dive relevance against an explicit opponent field. Do not treat the above conditional percentages as real-game win-rate effects.
