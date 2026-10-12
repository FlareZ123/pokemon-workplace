# Aichi champion Shadow Rider: Mysterious Treasure discard-payment frontier

## Question

The [2026 Aichi champion Shadow Rider Calyrex list](../competitive_deck_baselines/)
uses four Mysterious Treasure to search for Psychic or Dragon Pokémon,
including Radiant Eternatus. The [exact Radiant launch model](../shadow_rider_radiant_launch/)
counts **31.681322310%** of Basic-valid going-second starts as successful
two-VMAX setups through Treasure. Yet each Treasure requires discarding another
card *before* the search. How does that route change when only specified hand
cards are strategically acceptable discards?

## Findings

The answer depends sharply on the player's discard policy, even while
the deck remains the **same exact legal 60-card champion list**.

The source inventory has 11 Psychic Energy, four Mysterious Treasure, and
37 other cards outside the Radiant / VMAX / Treasure / Heavy Ball / other-Basic
opening categories. To study state-dependent discard acceptability, designate
K of those 37 as acceptable cost cards. This is a **hypothetical property
assignment**, not a statement that every Energy card is disposable.

Two illustrative policies are compared:

- **Strict filler-only:** one of the K acceptable filler cards must be
  physically in hand after the first natural draw.
- **Filler or spare Treasure:** alternatively, a second Mysterious Treasure
  held in hand may be discarded to pay for the first.

| K accepted filler copies | Strict filler only | Filler or spare Treasure |
| ---: | ---: | ---: |
| 0 | 0.000000% | 5.647245% |
| 4 | 12.739312% | 16.398764% |
| 11 | **24.843972%** | **26.390182%** |
| 37 | 31.672377% | 31.677412% |
| No discard-value restriction | **31.681322%** | **31.681322%** |

All percentages are unconditional on the named route and conditional on an
accepted seven-card Basic opening plus the first going-second draw.
Direct Radiant and Hisuian Heavy Ball routes are untouched.

**Hypothetical Psychic-Energy payment.** The champion list has exactly
11 Basic Psychic Energy. If one treats those 11 as the only acceptable
cost candidates, Treasure's contribution to two-VMAX access falls from
31.681322% to **24.843972%**. Allowing spare held Treasure as the
alternative raises it to **26.390182%**. Psychic Energy may be needed
for attacks and Underworld Door, so this is a diagnostic policy, not an
endorsement of discarding Energy in actual games.

Combining the latter scenario with the independently measured direct
Radiant (12.017840%) and Heavy Ball (1.238782%) routes gives a modeled
**39.646803%** two-VMAX access event. Under the strict Energy-only payment
choice it is **38.100594%**. Against the unrestricted
44.937944% launch ceiling, this exposes the possible magnitude of resource
conservation without assuming a single scalar DCI value is universally
correct.

## Exact derivation

Implementation: `tools/shadow_rider_treasure_cost_sensitivity.py`  
Reproducer: `results/shadow_rider_treasure_payability/reproduce.py`  
[Passing Windows CI 38242634153](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38242634153)

The same source-checked six-category physical start/Prize/draw enumerator
from the [Heavy Ball study](../shadow_rider_heavy_ball_launch/) is reused.
It aggregates exact integer weights by just two post-draw hand features:
number of the 37 generic filler cards held, and number of Mysterious
Treasure copies held.

Conditional on h held cards sampled uniformly from the 37-card filler
pool, K acceptable copies appear with exact probability

`1 - C(37-K, h)/C(37, h)`.

When a second Treasure is held, its own discard can be an alternative
payment. Each hand-signature weight is multiplied by the appropriate
acceptance probability, giving an exact rational result. No approximate
Monte Carlo weighting is used.

As an independent oracle, a ten-card toy pool with explicit physical
card-instance identities is exhaustively enumerated through 8,925 accepted
opening/Prize/draw worlds. Its safe-filler identities are marked one by one.
For all K in 0..3 and for both payment policies, the physical frequencies
agree **exactly** with the grouped conditional hypergeometric calculation.
The regression also checks the full actual-list 31.681322310% unrestricted
Treasure route and monotonicity for every K in 0..37.

## Why this matters

The earlier graph-access statement "Mysterious Treasure can find Radiant"
does not imply the player can afford to discard a strategically acceptable
card in every hand. The sensitivity curve separates **mechanical payability**
from **opportunity-cost acceptance**, complementing the prior research on
state-dependent DCI and connector domination.

## Limits

Only the named first-turn `Treasure -> Radiant -> Climactic Gate -> two
Shadow Rider VMAX` line is priced. Initial Active selection, post-Prize
VMAX stock, first natural draw, and source counts match the previous exact
analysis. The model does not choose a card with state-dependent future
value, analyze hand-to-Bench alternatives, consume Energy as attack supply,
model opposing locks, or estimate game/match win rates. A more complete
planner should condition acceptable discard identities on opponent,
current board, K0/K1 information and intended attacking plan.
