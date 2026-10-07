# Exact named-line probability for Aichi Iron Thorns ex

## Question

For the three published Iron Thorns ex lists from the 2026 Aichi Open League, what is the exact first-turn-going-second probability of reaching the named attack line:

`Tag Call -> Guzma & Hala -> Thunder Mountain Prism Star + Double Colorless Energy -> Volt Cyclone`

when only natural access, Tag Call, and Guzma & Hala are counted?

This result deliberately excludes Trainers' Mail and other draw or search effects so the probability corresponds to a narrow, auditable ALS core rather than a full turn simulator.

Implementation: `tools/iron_thorns_named_line_probability.py`  
Regression: `results/iron_thorns_named_line_probability/reproduce.py`

## Published list structure

The repository's Aichi list transcription records all three Iron Thorns lists as having exactly four Pokémon, all four copies of Iron Thorns ex. The relevant counts are:

| Player | Iron Thorns ex | Tag Call | Guzma & Hala | Thunder Mountain Prism Star | Double Colorless Energy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kazuma Kashi | 4 | 2 | 2 | 1 | 1 |
| Ryoya Fujii | 4 | 2 | 2 | 1 | 3 |
| Kohei Hamamichi | 4 | 2 | 2 | 1 | 1 |

The remaining cards are grouped as filler for this exact narrow-line calculation.

## Setup model

Each state is generated exactly by combinations:

1. draw a seven-card opening hand;
2. condition on the hand containing at least one Iron Thorns ex;
3. choose one Iron Thorns ex as the Active Pokémon;
4. set six Prize cards from the remaining deck;
5. draw one card for the first turn going second.

The calculation does not sample Monte Carlo states. Every category composition is weighted by its exact number of labeled realizations.

Opponent mulligan bonus draws are omitted.

## Success definition

The named line succeeds if, after the first-turn draw, one of these conditions holds:

- Thunder Mountain and Double Colorless Energy are both already in hand; or
- every missing one of those resources is still searchable in the deck, and Guzma & Hala is accessible either directly from hand or through Tag Call from hand while a Guzma & Hala remains in the deck.

If Double Colorless Energy must be searched by Guzma & Hala, the optional two-card discard branch is required.

The model treats the two-card discard cost as mechanically payable in these no-prior-action states. After selecting the Active Pokémon and drawing for the turn, the player has seven other hand cards. Playing Tag Call and taking one Guzma & Hala is hand-size neutral. Playing Guzma & Hala then leaves enough other cards to discard two.

This is a mechanical statement only. It does not assert that those cards are strategically acceptable discards under DCI.

## Exact result

The probability of an accepted opening with four forced Basics is:

**39.949962574%**

Conditioned on such an accepted opening:

| Published list | DCE copies | Named line succeeds |
| --- | ---: | ---: |
| Kazuma Kashi | 1 | **33.781505711%** |
| Ryoya Fujii | 3 | **39.107850627%** |
| Kohei Hamamichi | 1 | **33.781505711%** |

Ryoya's three-DCE construction gains **5.326344917 percentage points** in this narrow named-line model relative to the otherwise identical relevant 2 Tag Call / 2 Guzma & Hala / 1 Thunder Mountain / 1 DCE structure.

This is a route-specific access gain, not a claim about overall deck strength.

## Failure-mode decomposition

### One-DCE structure: Kazuma and Kohei

| State class | Probability |
| --- | ---: |
| Direct Thunder Mountain + DCE in hand | 1.278355134% |
| Guzma & Hala mediated, DCE must be searched | 28.940230640% |
| Guzma & Hala mediated, DCE already in hand | 3.562919937% |
| Required Thunder Mountain or DCE unavailable from hand/deck | 19.411781176% |
| Resources available, but Guzma & Hala connector unavailable | 46.806713113% |

The three success rows sum to **33.781505711%**.

Most success mass, 28.940230640 percentage points, passes through Guzma & Hala's two-card discard branch. That makes discard quality strategically important even though the exact mechanical model has enough hand cards to pay the cost.

### Three-DCE structure: Ryoya

| State class | Probability |
| --- | ---: |
| Direct Thunder Mountain + DCE in hand | 3.499747698% |
| Guzma & Hala mediated, DCE must be searched | 25.894650078% |
| Guzma & Hala mediated, DCE already in hand | 9.713452851% |
| Required Thunder Mountain or DCE unavailable from hand/deck | 10.199548960% |
| Resources available, but Guzma & Hala connector unavailable | 50.692600413% |

The extra Double Colorless Energy copies substantially reduce the unavailable-resource class, from 19.411781176% to 10.199548960%.

The connector-failure percentage becomes larger because the resource-zone failure class shrinks. This is a conditional decomposition of the same total state space. It does not mean extra DCE makes connector access worse.

## Finding 1: singleton Prize risk and connector risk are distinct

A state can fail because Thunder Mountain or all represented Double Colorless Energy copies are unavailable from both hand and deck.

A different state can have every required resource available while lacking a current route to Guzma & Hala.

These failure classes should be modeled separately. Increasing the DCE count attacks the first class directly. It does not create another Tag Call or Guzma & Hala out.

## Finding 2: extra DCE changes more than Prize resilience

Three DCE copies improve several channels at once:

- more openings naturally contain DCE;
- more post-Prize decks retain at least one searchable DCE;
- more states need Guzma & Hala only for Thunder Mountain rather than for both resources;
- more success states avoid Guzma & Hala's optional discard branch.

The gain is therefore larger than a simple singleton-Prize correction.

## Finding 3: the narrow ALS remains connector-limited

Even with three DCE copies, just over half of the accepted-opening states fall into the category where the needed resource package exists but the named G&H access route is absent.

That identifies a natural next modeling target: Trainers' Mail. All three published lists contain Trainers' Mail, and it can expose additional Trainer access before the Supporter is committed.

A broader model should quantify how much of this connector-failure mass is actually recoverable through those additional transitions.

## Validation

The implementation uses exact integer combination weights and returns `Fraction` values.

The regression also constructs a separate labeled ten-card toy deck with:

- two forced Basics;
- one Tag Call-like connector;
- one Guzma & Hala-like Supporter;
- one Thunder Mountain-like resource;
- one DCE-like resource;
- four filler cards;
- a three-card opening;
- two Prize cards;
- one turn draw.

An independent exhaustive enumeration over every accepted labeled opening, disjoint Prize selection, and draw produces exactly:

`563 / 1680 = 33.511904762%`

The grouped exact model produces the same fraction.

## Limits

This result is intentionally narrower than the deck's true first-turn attack probability.

It excludes:

- Trainers' Mail;
- other draw Supporters and draw effects;
- opponent mulligan bonus draws;
- alternative Stadium or Energy lines;
- Speed Lightning Energy draw effects;
- Prize rescue;
- any route that attacks without the Thunder Mountain + DCE package;
- strategic preservation of hand cards under DCI;
- opponent disruption;
- post-attack value.

The numbers should therefore be read as exact probabilities for the named ALS under the stated action set.

## Next useful work

Add Trainers' Mail to the same setup-conditioned state model while preserving:

- actual top-four lookups;
- shuffle-after-search behavior;
- Supporter timing;
- current hand size for Guzma & Hala's discard branch;
- Thunder Mountain and DCE zone state;
- multiple Trainers' Mail copies.

That extension would show how much of the current connector-failure mass converts into real first-turn Volt Cyclone access.
