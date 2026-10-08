# Exact fixed-slot frontier: Nest Ball, Super Scoop Up, Scoop Up Cyclone

## Question and experimental objective

Under the restricted single-support pickup-replay access model, how should
eight flexible deck slots be allocated among direct-to-Bench Basic search,
coin-flip pickup Items, a deterministic ACE SPEC pickup, and expendable
discard-payment cards?

This is a small **access-only frontier**, conditional on an accepted
opening hand. It tests the interaction of the number of outs available,
Quick Ball payments, Bench entry from the correct zone, Active recovery,
and pickup-coin outcomes. It does not optimize whole-deck performance.

- Exact enumerator and independent prior state solver:
  [reproduce.py](reproduce.py)
- Underlying action model:
  [bench_trigger_paid_replay.py](../../tools/bench_trigger_paid_replay.py)
- Mechanism study:
  [paid pickup replay](../bench_trigger_paid_replay/)

## Fixed conditions

A 60-card deck contains one singleton support A with a from-hand
Bench-entry Ability, three other ordinary Basic starters, and four
Quick Ball copies. Other than the eight flexible slots, all remaining
cards are inert filler. The eight slots must contain:

- `N` Nest Ball-like direct-to-Bench search Items, between 0 and 4;
- `R` Super Scoop Up-like fair-coin pickups, between 0 and 4;
- `G` Scoop Up Cyclone deterministic pickup, either 0 or 1;
- `X = 8 - N - R - G` deliberately disposable filler cards.

Other deck cards are treated as strategically protected unless specifically
counted as Quick Ball payment resources. Nest Ball and pickup Items can
be discarded to pay Quick Ball instead of being played.

The deck starts with a seven-card hand and six face-down Prizes, followed
by one additional random card. This is the same restricted accepted-opening
model used in earlier Agent15 results. The optimizer resolves legal action
orders and conditional coin outcomes using exact rational arithmetic.

The number of eligible packages is **49**.

## Search result

| Rank | Nest Ball | Super Scoop Up | Scoop Up Cyclone | Disposable filler | Exact access |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 3 | 1 | 0 | **35.787079%** |
| 2 | 3 | 4 | 1 | 0 | 35.535984% |
| 3 | 3 | 3 | 1 | 1 | 34.588451% |
| 4 | 4 | 2 | 1 | 1 | 34.552353% |
| 5 | 4 | 4 | 0 | 0 | 34.410901% |
| 6 | 2 | 4 | 1 | 1 | 33.974038% |

Within this precisely defined goal, the highest-scoring package contains
four Nest Balls, three Super Scoop Ups and one Scoop Up Cyclone.

The best package with no ACE SPEC is four Nest Balls and four Super
Scoop Ups, at **34.410901%**. Replacing one of those Super Scoop Up
copies with the deterministic Scoop Up Cyclone increases restricted
access to **35.787079%**, an improvement of **1.376178 percentage points**.

This is a conditional card-package gain; it is **not a recommendation**
to spend the ACE SPEC allowance on Scoop Up Cyclone in a real deck.
Replacing Computer Search, Secret Box, or another ACE SPEC could have a
much larger effect on attacker setup, Energy access, disruption or the
match's win condition.

## Why this differs from simple pickup counts

A single guaranteed pickup is more reliable once available, but appears
in fewer random hands than four separate coin pickup copies. Nest Ball
competes for the same flexible slots, while being useful in three
different roles: Quick Ball payment, support-A pickup replay, and
backup-Basic placement enabling Active-A rescue.

The optimal package emerges from the joint distribution of visible
search/pickup cards, Prize configurations, payments, and the scheduler's
ability to choose actions in response to Super Scoop Up coin outcomes.
The regression enumerates **all 49 allowed integer packages** rather
than using a heuristic marginal-out count.

## Limits and validation

This frontier inherits the exact paid-replay kernel's tested
8,925-labeled-world oracle and ten action-state witnesses.
The package enumerator separately asserts the complete count and exact
winners with and without an ACE SPEC.

The model omits real Ability hand changes, Item/Ability locks, card
interactions outside the named classes, the strategic cost of protecting
the ACE SPEC slot, opponent turns, and the effects of allocating those
eight flexible cards to other useful Trainers or Energy.

A more realistic deck optimizer would attach a matchup-sensitive
opportunity cost to each slot and the ACE SPEC itself, then score
successful game plans rather than a single support's trigger availability.
