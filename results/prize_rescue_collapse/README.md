# Prize-rescue collapse: exact combinatorial baseline

## Question

How often can an apparently redundant Prize-recovery package still fail because several important singleton cards and the recovery cards themselves are trapped in the initial Prize cards?

This result formalizes one narrow part of the multi-prized-collapse idea in `resources/human_concepts.md`. It is an exact setup-Prize model rather than a full game simulator.

## Card-text basis

The bundled Expanded card pool contains two prints of `Gladion` (`sm4-95` and `sm4-109`), both marked Expanded legal in the local database. Its relevant text is:

> Look at your face-down Prize cards and put 1 of them into your hand. Then, shuffle this Gladion into your remaining Prize cards and put them back face down.

The bundled advanced manual also states that a player may use only one Supporter during a turn.

Two consequences matter for this model. A Gladion copy outside the Prize cards can recover one critical Prized card. After that use, the Gladion itself becomes a Prize card, so that same copy cannot provide another rescue before some later Prize-taking or other recovery event brings it back.

## Exact model

Let:

- `N` be deck size;
- `P` be the number of initial Prize cards;
- `C` be the number of distinct critical singleton cards in the deck;
- `G` be the number of Gladion copies;
- `c` be the number of critical singletons among the initial Prize cards;
- `g` be the number of Gladion copies among the initial Prize cards.

The exact joint probability of a Prize configuration is

`choose(C, c) * choose(G, g) * choose(N - C - G, P - c - g) / choose(N, P)`.

At setup, `G - g` Gladion copies are outside the Prize cards. Under the modeled horizon, each can recover one critical singleton before becoming a Prize itself. The package therefore collapses when

`c > G - g`,

or equivalently when

`c + g > G`.

The implementation is `tools/prize_rescue_collapse.py`. It computes the exact joint distribution, unconditional collapse probability, conditional collapse probability given that at least one critical singleton is Prized, and a breakdown of the specific collapsing states. `results/prize_rescue_collapse/reproduce.py` regenerates the tables below and runs an exhaustive small-deck validation.

## One critical singleton

For a 60-card deck with 6 Prize cards:

| Gladion copies | Unconditional collapse | Collapse given singleton is Prized |
| ---: | ---: | ---: |
| 1 | 0.84746% | 8.47458% |
| 2 | 0.05845% | 0.58445% |
| 3 | 0.00308% | 0.03076% |
| 4 | 0.00011% | 0.00110% |

With one critical singleton, collapse requires that singleton and every Gladion copy to be Prized together. Two Gladion copies reduce this specific topology failure to about 0.058% of all games. Conditional on the singleton actually being Prized, the risk is about 0.584%.

A third Gladion reduces the unconditional risk by a factor of 19, to about 0.00308%. The absolute conditional improvement from the second to the third copy is about 0.554 percentage points. In a deck where Prize insurance for one singleton is the only reason to include the third copy, this exact failure mode alone supplies little justification for the slot.

That conclusion changes as the number of independently critical singleton cards increases.

## Multiple critical singletons

The next table conditions on at least one modeled critical singleton being Prized.

| Critical singletons | 1 Gladion | 2 Gladion | 3 Gladion | 4 Gladion |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 8.47458% | 0.58445% | 0.03076% | 0.00110% |
| 2 | 12.66402% | 1.17245% | 0.07801% | 0.00339% |
| 3 | 16.81349% | 1.95875% | 0.15818% | 0.00813% |
| 4 | 20.91669% | 2.94321% | 0.28047% | 0.01671% |
| 5 | 24.96721% | 4.12476% | 0.45439% | 0.03089% |

This exposes a limitation of evaluating Gladion counts against only one headline singleton. With four separate critical singletons, two Gladion copies leave a 2.943% collapse probability in the subset of games where at least one of those cards is Prized. Three Gladion copies lower that figure to 0.280%.

The mechanism is broader than every Gladion being Prized. For example, with three critical singletons and two Gladion copies, collapse can occur when two critical cards and one Gladion are Prized together. It can also occur when one critical card and both Gladion copies are Prized, or when three critical cards are Prized even if both Gladion copies remain outside the Prize cards.

## How often does the recovery problem arise?

For 60 cards and 6 Prize cards, the probability that at least one modeled critical singleton is Prized is:

| Critical singletons | At least one is Prized |
| ---: | ---: |
| 1 | 10.00000% |
| 2 | 19.15254% |
| 3 | 27.51607% |
| 4 | 35.14596% |
| 5 | 42.09461% |

A conditional collapse rate therefore needs to be read together with how often the deck enters a state that needs Prize recovery at all.

## Strategic interpretation

### Derived result

Prize protection is a package-level property. The reliability of a recovery card depends on how many distinct resources may simultaneously require rescue and on whether the recovery cards themselves occupy Prize slots.

This gives a quantitative form to multi-prized collapse. A statement such as "two Gladion protect the ACE SPEC" is incomplete when the same Gladion copies may also need to recover other matchup-critical or setup-critical singletons.

### Relation to K0 and K1

The calculation concerns the hidden initial Prize configuration itself. Once the player reaches a state where the Prize contents are known or strongly inferred, the exact realized values of `c` and `g` can guide whether a rescue line exists. Before that information is available, the table describes the ex ante risk.

### Relation to AMR and Supporter contention

This model only asks whether enough rescue copies exist outside the Prize cards. It does not guarantee that those copies are realistically accessible or playable. A Gladion still consumes the Supporter for the turn, can be blocked by Supporter lock, and may compete with another Supporter needed for setup or Energy acceleration. The numbers here are therefore a Prize-topology ceiling on rescue availability rather than a complete AMR estimate.

## Validation

The implementation was checked in two independent ways:

1. For one critical singleton, the general summation matches the direct closed form in which the singleton and all Gladion copies must be among the six Prize cards.
2. A small `N=12`, `P=4`, `C=3`, `G=2` case was exhaustively enumerated over all `choose(12, 4) = 495` Prize sets. The exhaustive result exactly matched the library calculation: `0.151515151515...`.

The joint probability mass was also checked to sum to one across tested parameter ranges.

## Limitations

This model isolates the initial Prize topology. It does not simulate opening hands, mulligans, draw or search access to Gladion, ordinary Prize-taking, alternative Prize-recovery cards, attacks that take extra Prizes, lock effects, matchup-dependent criticality, or turns where some singleton stops mattering.

All modeled critical cards are treated as requiring recovery before ordinary Prize-taking can be relied on. That assumption is appropriate for setup-critical resources and conservative stress tests. It can overstate practical risk when a Prized card is only needed later in the game.

The calculation also assumes every Gladion copy outside the Prize cards can eventually be reached and played. Real Supporter access can be substantially worse, so this result should be combined with search, draw, sequencing, and Supporter-contention models for deck-specific conclusions.

## Next useful work

A stronger deck-level model would label actual singleton resources by when they become critical, combine this Prize-state calculation with a search-access model for Gladion, and allow competing Supporter lines. It could then estimate the probability that a deck reaches a required resource by a specific turn instead of only measuring the initial Prize topology.
