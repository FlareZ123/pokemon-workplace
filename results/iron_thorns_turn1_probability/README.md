# Exact first-turn Volt Cyclone probability for the Aichi Iron Thorns list

## Question

How often does the named Iron Thorns ex ALS reach Volt Cyclone on the first turn going second when opening hands, six Prize cards, and the first draw are modeled exactly?

This result uses Kazuma Kashi's sixth-place Iron Thorns list from the 2026 CL Aichi Open League.

Implementation: `tools/iron_thorns_turn1_probability.py`

Reproducer: `results/iron_thorns_turn1_probability/reproduce.py`

## Scoped package

The exact list has:

- 4 Iron Thorns ex;
- 2 Guzma & Hala;
- 2 Tag Call;
- 1 Thunder Mountain Prism Star;
- 1 Double Colorless Energy;
- 1 Gladion.

The probability space conditions on an accepted seven-card opening. Since Iron Thorns ex is the list's only Basic Pokémon, one of the four copies becomes the starting Active. Six Prize cards are then sampled and one card is drawn for the first turn.

The calculation uses exact multivariate hypergeometric opening and Prize allocations, followed by the exact first-draw probability.

## Baseline named route

The baseline permits two routes.

A direct route succeeds when both Thunder Mountain and Double Colorless Energy are already in hand.

The Guzma & Hala route succeeds when Guzma & Hala is in hand, or Tag Call in hand can fetch a Guzma & Hala still in the deck, and every missing member of the Thunder Mountain plus Double Colorless package remains searchable from the deck.

Guzma & Hala's two-card optional discard is mechanically payable in this timing model. At the start of the first turn the player has seven cards in hand after promoting one opening Basic and drawing. Playing Guzma & Hala directly, or playing Tag Call and then Guzma & Hala, leaves six other cards available before the optional discard.

The exact accepted-opening probability of reaching the attack through these represented routes is **33.781505711%**.

Its successful mass separates into:

- direct Thunder Mountain + Double Colorless in hand: **1.278355134%**;
- Guzma & Hala package: **32.503150577%**.

This is a scoped route probability rather than a claim about every possible line in the 60-card list.

## K0/K1 extension with Gladion

Gladion creates an information problem.

Before the first deck search, the player is in a K0-like state and does not know whether an absent singleton is in the deck or in the Prize cards. If Guzma & Hala is available, choosing it is the attack-maximizing represented action when a required singleton is absent from hand because the missing singleton is much more likely to be in the deck than among six Prize cards.

Tag Call can change that state. When Tag Call is in hand and can fetch Guzma & Hala from the deck, the search exposes the deck contents and therefore the Prize composition by elimination before the Supporter is chosen. If exactly one attack-package singleton is Prized, the other is already in hand, and Gladion is also in hand, the player can switch from the planned Guzma & Hala line to Gladion.

The information-aware represented policy reaches Volt Cyclone in **34.008906144%** of accepted openings, an increase of **0.227400433 percentage points**.

The added successful mass is:

- Gladion as the only represented route to a Prized singleton: **0.181384268 points**;
- Tag Call establishes K1 and enables a Gladion pivot: **0.046016166 points**.

This is a concrete example where deck search has value beyond the card it fetches.

## Opponent mulligan bonus draws

The setup rules let a player draw bonus cards when the opponent mulligans. For this reachability objective, taking every available bonus draw is favorable.

`tools/iron_thorns_mulligan_bonus.py` extends the exact state enumeration by drawing the bonus cards after Prize placement and before the normal first-turn draw.

| Opponent mulligan bonus cards taken | Represented Volt Cyclone probability |
| ---: | ---: |
| 0 | 34.008906144% |
| 1 | 37.884578127% |
| 2 | 41.551388399% |
| 3 | 45.013092009% |
| 4 | 48.274114878% |
| 5 | 51.339472431% |
| 6 | 54.214691396% |

The first opponent mulligan therefore adds **3.875671983 percentage points** to this scoped first-turn attack probability.

This connects the public setup process to ALS consistency in two ways: mulligans expose information and the bonus cards can materially improve the executing player's resource access.

### Integrating the opponent's actual mulligan rate

A fixed bonus-card count is not the match-level probability. If an opponent has (B) forced setup Basics in a 60-card deck, its per-attempt mulligan probability is

`q(B) = C(60-B, 7) / C(60, 7)`.

Repeated failed openings form a geometric distribution before the opponent finally keeps. The model now integrates the represented Volt Cyclone probability over that full distribution.

For extremely long mulligan sequences, the player takes at most 46 bonus cards so one card remains for the mandatory first-turn draw. The probability mass of all longer sequences is collapsed onto that rational cap.

| Opponent | Forced Basics | Mulligan probability per attempt | Expected mulligans before keep | Matchup-adjusted Volt Cyclone | Gain over zero bonus |
| --- | ---: | ---: | ---: | ---: | ---: |
| Aichi Iron Thorns mirror | 4 | 60.050037426% | 1.503131256 | **39.378236642%** | +5.369330498 pp |
| Aichi runner-up Vileplume | 14 | 13.859068087% | 0.160888300 | **34.627066104%** | +0.618159961 pp |

The same deck therefore has materially different first-turn consistency before considering any opponent card effects. Opponent setup composition alone changes the distribution of extra cards available to the ALS.

This is a matchup-dependent setup effect: a low-Basic opponent can make the Iron Thorns line more consistent by mulliganing frequently, while a high-Basic opponent supplies much less bonus-card equity.

## What the result does not include

The model intentionally omits Trainers' Mail top-four lookups, other indirect access routes, opponent disruption after setup, and tactical reasons to prefer a different action even when Volt Cyclone is reachable.

It also treats the goal as binary first-turn attack reachability. It does not value the post-attack Energy move, board position, disruption, or matchup context.

Because the omitted routes can only add possibilities to this specific reachability question, the reported probability is best interpreted as an exact probability for the represented package rather than a complete deck-wide ceiling.

## Relationship to other results

`results/iron_thorns_integrated_als/` validates the action sequence and typed Energy endpoint.

`results/aichi_setup_inference/` models public mulligan information from this same tournament.

The present result adds full opening, Prize, and first-draw combinatorics and shows how K0/K1 changes the Gladion branch.
