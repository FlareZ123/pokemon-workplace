# Target-specific Retreat payment changes gust value

## Why extend the bounded escape model?

The earlier `results/defender_escape_gust/` gives the defender an abstract escape token. In real Expanded, the ability to retreat depends on the **currently Active Pokémon's** Retreat Cost, attached Energy cards, and restrictions. A Switch Item can provide a different route when ordinary retreat is unavailable, but its play can be forbidden by Item lock.

This study adds an explicit small physical payment state to the exact damage-aware, six-Prize, adversarial-promotion model. It isolates how much an escape gate's *location on the opposing board* matters.

## Model

`tools/typed_retreat_gust.py` represents each opposing Pokemon as:

`(Prize reward 1/2/3, hits to KO 1/2, effective Retreat Cost, attached Energy cards' generic units, retreat blocked)`.

A normal retreat is an option on the opponent's intervening turn after a non-KO hit only when not blocked, when a Benched replacement exists, and when a subset of **physical** Energy cards can pay the cost. Selected cards are discarded and the damaged Pokemon, with surviving Energy cards, moves to the Bench. Each attached Energy card has 1 or 2 generic units; a two-unit card may pay a one- or two-unit cost alone, but is still discarded as a whole card.

The implementation enumerates inclusion-minimal valid payment subsets rather than assuming all Energy cards are interchangeable or always discarding the fewest physical cards. This preserves strategic payment options such as using one two-unit card versus two single-unit cards to cover a cost of two. Cost zero permits retreat without discarding Energy.

An available `Switch`-like Item token instead switches to any Benched Pokemon without Energy payment, even if the outgoing Active cannot retreat. Such a token is usable only if `item_play_allowed` is true. The attacker still has 0, 1, or 2 gust tokens on different attack turns. The defender chooses its best retreat, Item switch, or stay option, maximizing the attacker's expected number of attacks, although all transitions here are deterministic.

Rules evidence: advanced manual A-03 (Retreat and attached Energy), C-01 (physical Energy discard), C-03 (switching bypasses retreat payment and prohibitions), and B-01/C-19 (Item play and Item lock). The existing repository retreat research additionally distinguishes Energy card count from units and handles modifier effects. The supplied `effective Retreat Cost` here is already resolved; this project does not recompute attached Tool/Stadium modifiers.

This remains a bounded opponent-endgame abstraction. It omits opponent attack pressure, new Bench Pokemon, manual Energy attachment on intervening turns, dynamic Energy providers, prizes drawn into hand, and time-varying lock states.

## Case study: which targets have one available Basic Energy?

Take the same 390 structural board classes as the earlier durable model: all two-to-four-Pokemon multisets of Prize values 1/2/3 and durability 1/2, with total Prize rewards at least six, and each distinct starting Active.

Give every Pokemon **Retreat Cost 1**. Compare four configurations of its attached Energy, each evaluated with no Switch Items:

- **None:** no Pokemon has Energy and none can retreat.
- **High:** each three-Prize Pokemon has one single-unit attached Energy.
- **Low:** each one-Prize Pokemon has one single-unit attached Energy.
- **All:** every Pokemon has one single-unit attached Energy.

| Attacks saved by two gusts | None | High | Low | All |
| --- | ---: | ---: | ---: | ---: |
| 0 | 122 | 145 | 120 | 171 |
| 1 | 105 | 132 | 112 | 134 |
| 2 | 126 | 85 | 117 | 57 |
| 3 | 30 | 24 | 34 | 24 |
| 4 | 7 | 4 | 7 | 4 |

Adding a single retreat-ready Energy to the three-Prize targets reduces the total two-gust attack-count benefit in **70 of 390 classes**. Attaching it instead to the one-Prize targets reduces the total two-gust benefit in only **6 classes**.

The direction makes tactical sense. Gust often specifically targets a high-Prize Pokemon whose two-hit KO represents the shortest Prize route; letting *that target* escape before the second hit matters far more often than enabling retreat on a lower-value Pokemon.

Strictly increasing marginal value from the second gust occurs in **107** no-Energy classes, **169** high-Energy classes, **109** low-Energy classes, and **159** all-Energy classes. Again, these are unweighted structural counts rather than real-world match frequencies.

## Concrete witness and Item lock contrast

Opponent Active `(1 Prize, 2 hits, Retreat Cost 1)`; Bench `(1 Prize, 2 hits)`, `(3 Prizes, 2 hits)`, `(3 Prizes, 2 hits)`.

If no Pokemon has any attached Energy, attack counts with 0/1/2 gusts are **(8,8,4)**. With one Basic Energy on each three-Prize target, the same counts become **(8,8,8)**, since the target can pay to retreat after the first hit. Giving Energy only to the one-Prize targets instead preserves **(8,8,4)**.

For a different escape route, set every Pokemon's normal retreat to blocked and give the defender one Switch Item. With Item play allowed, this exactly matches the earlier one-escape model. If an Item lock prevents the Switch from being played, the advantage reverts to the no-escape case.

One two-unit Energy is mechanically enough to pay a two-Colorless retreat cost, but must be discarded in its entirety. The regression verifies distinct residual physical-card sets for a two-unit card plus two or three single-unit cards.

## Verification

`results/typed_retreat_gust/reproduce.py` checks a second, Boolean turn-deadline game tree on **4,680** board/access configurations: 390 boards times 4 Energy-placement regimes times 3 gust budgets. It also performs **3,510 cross-kernel checks** against `durable_gust_minimax` and `defender_escape_gust` for the equivalent no-retreat and blocked-retreat Item-switch regimes.

The reproducer asserts all four distributions, counts of increasing marginal gust value, the 70-versus-6 target-placement asymmetry, energy-card payment alternatives, and the explicit witnesses.

Reproduce from repository root: `python results/typed_retreat_gust/reproduce.py`.

## Limits and next steps

Conditioning on one attached Energy card is deliberately narrower than modeling a real deck's Energy acceleration, board state, Retreat Cost modifications, attached Energy provider legality, and Item-lock effects. A stronger bridge can project a live `BoardState` into target-specific legal retreat candidates using the repository's `board_derived_retreat.py` and `retreat_energy_transaction.py` rather than manually supplying the effective cost and energy units.

The result argues for opponent counterplay that is resolved *per target, at the turn it matters*, rather than one fixed numerical escape penalty attached to an archetype.
