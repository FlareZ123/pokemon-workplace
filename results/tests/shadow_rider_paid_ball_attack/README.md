# Aichi champion: Energy-paid Ball access to Radiant, then next-turn Max Geist

## Competitive question

The [published Aichi 2026 champion Shadow Rider Calyrex 60](../../decks/shadow-rider-calyrex/) includes one Radiant Eternatus, four Mysterious Treasure, one Quick Ball, four Shadow Rider VMAX, eleven Basic Psychic Energy, a single Float Stone and a single Dimension Valley. Earlier [direct Radiant launch](../shadow_rider_direct_launch_attack/) and [exact Stadium/Float access](../shadow_rider_valley_pivot_gate/) studies deliberately excluded search sources. This extension evaluates the champion's **five one-discard Ball sources** as an additional route to Radiant, preserving payment costs and the competing second-turn attack Energy requirements.

Both Mysterious Treasure (sm6-113) and Quick Ball (swsh1-179) can search the specific Radiant Eternatus Dragon Basic, and each demands one discard from hand. Their search targets and alternate uses differ in general. For this narrow Radiant endpoint, we group them into five physically distinct equivalent one-discard sources. We require that discard to be a held **Basic Psychic Energy**, rather than assuming any hand card can be sacrificed. This is a deliberately conservative payment policy.

## Defined sequence and policy

Draw an opening seven conditioned on containing any legal starting Basic; set six Prize cards. To use Radiant's hand-to-Bench Climactic Gate, a **non-Radiant Basic must occur in the actual opening seven** and occupy Active. Take one natural draw going second. The policy selects the following first-turn route:

- **Direct route:** Radiant is already held or is drawn naturally. Play it onto Bench and use Climactic Gate without search-payment cost.
- **Paid Ball route:** Radiant is still in deck, at least one of the five search Items and one Basic Psychic Energy are in hand, and two VMAX are available in deck. Play one search Item, discard one Psychic, fetch Radiant, then play Radiant and launch two VMAX.

Both routes consume the first turn because Climactic Gate ends it. On the following **uninterrupted** turn, draw a natural card, use at most two Underworld Door Abilities (each attaches a Psychic from hand to the target Benched VMAX and draws two), and finally make one normal Energy attachment. Charge an initially unpowered VMAX while it remains Benched and require a later legal promotion. The exact model separately requires enough Energy for normal three-cost Max Geist and allows two-cost Max Geist when a physically accessible Dimension Valley can be legally played. It also evaluates a restricted Float Stone-only pivot, with no alternative movement.

The Ball search removes **one more physical card from the deck** than the direct route and discards a Psychic Energy before the following turn. This changes the size and composition of the remaining deck, the chance of later Ability activations, and the probability of actually reaching attack readiness.

## Exact full-60 results per accepted opening

| Event | Direct Radiant | Psychic-paid Ball | Combined disjoint routes |
| --- | ---: | ---: | ---: |
| Launch two VMAX | 12.017840120% | 29.446836494% | **41.464676614%** |
| Also charge normal three-Energy Max Geist next turn | 4.455846832% | 5.251226541% | **9.707073373%** |
| Also access Float Stone for the normal-cost pivot | 0.768862128% | 0.843495738% | **1.612357866%** |
| Reduced two-Energy charge + found Valley + Float Stone | 0.216450306% | 0.273466613% | **0.489916919%** |
| **Either normal or Valley-assisted Float Stone route** | 0.866274545% | 0.997723737% | **1.863998282%** |

Direct and paid categories are mutually exclusive because paid Ball is attempted only if Radiant is not naturally observed. The last line is the *union* of normal and reduced-cost paths, subtracting outcomes in which both conditions are satisfied. It cannot be interpreted as a match win rate.

A strategic distinction: conditional on the relevant launch already succeeding, three-Energy Max Geist readiness is **37.076936%** for direct launch versus **17.832906%** for the Energy-paid Ball launch. The paid route improves opening reach but consumes Psychic Energy that would otherwise have contributed to next-turn attack readiness. This is a concrete example of search access and physical payment resources competing.

The narrow Float Stone union is 7.208238% conditional on direct launch and 3.388220% conditional on paid search launch. That difference is driven by the defined payment and resulting conditional hand composition, without considering the actual deck's richer search, draw, and pivot network.

## Exact methodology and verification

[tools/shadow_rider_paid_ball_attack.py](../../../tools/shadow_rider_paid_ball_attack.py) partitions the published 60 into seven print-grounded card groups: Radiant1, other starting Basics13, VMAX4, Basic Psychic11, Float Stone1, Ball sources5 and neutral25. Exactly one of those neutral cards is Dimension Valley. It enumerates all group-composition opening seven cards, six Prize cards, first natural draw, physical payment route and following natural draw. A Ball payment removes a Psychic from hand and one additional Radiant from the deck. The resulting conditional hands and shuffled-deck compositions pass to the validated exact Energy/Float/Valley multivariate-hypergeometric continuation, in which one Underworld Door must have Psychic available to trigger its subsequent two-card draw. The distinct next-draw denominators for direct and Ball launches preserve physical deck cardinality.

The [reproducer](reproduce.py) checks exact champion fractions, proves the unchanged direct route numerically agrees with the preceding independent model, and matches **four fully enumerated physical-card toy decks** using a separate algorithm that actually removes card IDs for the paid Ball and discarded Psychic. It also verifies the bundled printed one-discard search texts and the four-plus-one search counts in the champion's deck. Tests passed locally on 12 October 2026. GitHub Actions or end-to-end Twinleaf match validation is not asserted.

## Limitations and next experiment

The restricted payment policy discards **only a Basic Psychic Energy**, leaving out numerous other strategically acceptable discard targets. The model does not route Hisuian Heavy Ball into Prize recovery, use Forest Seal Stone, let Mysterious Treasure search for other Pokémon, or permit any alternate draw/discard sequencing before the launch. It does not price Tapu Lele-GX's Wonder Tag, Latias ex's free retreat, Guzma, Shadow Rider's own Forest Seal Stone, Tool and Ability locks, Stadium replacement versus Sky Field, an adversarial intervening opponent turn, or Max Geist damage/KO utility.

The next improvement should add the champion's actual other pivot routes and search payment choices, preserving shared Supporter windows, Prize risks and Bench occupancy. Separately, matchup-aware testing should compare the attack-ready board's probability of surviving the intervening turn, rather than treating an access endpoint as an achieved knockout or win.
