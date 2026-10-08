# Paired-switch order is a game-state constraint, not a generic gust tag

## Question

The [Trainer gust catalog](../trainer_gust_catalog/) already distinguishes
targeted opposing switches and flags several cards that also switch your own
Active Pokemon. Is `own_switch` alone a sufficiently precise label to
determine whether the opponent gust actually occurs?

**No.** Four paper Expanded Trainer card names have paired own/opponent
switches, but their conditional ordering is different. Some attempt the
opponent switch first and preserve it even without an own Bench. Another
requires a successful own switch before the opponent switch happens.

## Printed examples and source audit

The bundled current-English card snapshot and legality overlay contain
**11 Expanded-legal print records** across the following four names:

| Card | Legal print records | First switch | Conditional second switch | Other required action resource |
| --- | ---: | --- | --- | --- |
| Prime Catcher | 2 | Opponent's Bench to Active | Your Active with own Bench | ACE SPEC Item |
| Cross Switcher | 1 | Opponent's Bench to Active | Your Active with own Bench | Two copies played together, Item |
| Guzma | 4 | Opponent's Bench to Active | Your Active with own Bench | Supporter |
| Team Rocket's Giovanni | 4 | Your Active Team Rocket's Pokemon with own Benched Team Rocket's Pokemon | Opponent's Bench to Active | Supporter |

All four use a variant of *If you do* to make the second switch
conditional on successfully executing the first.

Official Prime Catcher card text:
https://asia.pokemon-card.com/sg/card-search/detail/12247/

The Advanced Player's Rulebook II-A and E-20 distinguish a second effect
that depends on first-effect success. If the first effect occurs, a second
effect that cannot happen is ignored without undoing the first. If the
first effect fails completely, the dependent second effect does not happen.

## The opposite Bench-side asymmetries

### Opponent has a legal target; your own Bench is empty

The opponent-first cards **Prime Catcher, Cross Switcher, and Guzma** can
execute the opponent gust; their own switch is impossible because there
is no Benched Pokemon to promote, so the effect stops after opponent gust.

**Team Rocket's Giovanni** cannot perform its first step without a
Benched Team Rocket's Pokemon (and an Active Team Rocket's Pokemon).
Consequently, its opponent gust never executes, even when the opponent
has several vulnerable Bench targets.

### Opponent has no eligible Bench target; your own Team Rocket board is ready

The direction reverses. The opponent-first cards cannot accomplish their
first switch and therefore do not execute their dependent own switch.

Team Rocket's Giovanni can complete its first own Team Rocket switch,
then fail the opponent step if the opponent has no eligible Bench target.
Its own switch still occurs. Whether using the Supporter for only that
switch is strategically worthwhile is a separate question.

### Both sides have valid targets

The first three cards resolve `opponent -> own`. Team Rocket's Giovanni
resolves `own -> opponent`.

The game actions are different even if both end with each player having
switched their Active Pokemon. In particular, intermediate state,
trigger timing, and whether the second switch is legal can depend on
which action occurred first.

## Executable representation

`tools/paired_switch_order_catalog.py` stores each card's ordered
two-stage effect, whether two card copies must be played together, and
whether the own first switch requires Team Rocket's Pokemon. It returns
an ordered effect sequence from explicit eligibility predicates:

- `("opponent",)`
- `("opponent", "own")`
- `("own",)`
- `("own", "opponent")`
- or an empty sequence.

The function is deliberately an **effect-order resolver**, not a complete
Trainer play validator or a physical board executor. It does not spend the
Supporter window, remove Item cards, check Item lock, move physical
Pokemon, or determine whether the source is accessible in hand.

It complements the detailed Prime Catcher attack-readiness result:
[prime_catcher_order_geometry/](../prime_catcher_order_geometry/).

## Validation

The regression:
- imports the existing legality-filtered `trainer_gust_catalog.catalog()`;
- identifies **2 Prime Catcher, 1 Cross Switcher, 4 Guzma, and 4 Team
  Rocket's Giovanni** legal print rows;
- verifies literal source text orders the two switch clauses around
  `If you do` correctly in all 11 print records;
- compares the generic ordered resolver against an independently written
  card-name-specific interpreter on 48 distinct geometry and Team Rocket
  eligibility combinations;
- asserts key opponent-only, own-only, and both-switch scenarios.

Reproduction file:
`results/paired_switch_order_catalog/reproduce.py`.

## Strategic consequence

Any resource graph or move compiler that collapses these cards to a generic
`targeted opponent gust + self-switch` action will mis-evaluate at least
some empty-Bench or eligibility states.

The execution model should preserve **action order**, **conditional
dependency**, and **source-specific own-side eligibility**. The number
of gust options theoretically in hand cannot substitute for those
requirements.

## Scope limits

The card snapshot is English Expanded-legal according to the repository's
current overlay, and may omit Japanese-only cards and prints. The model
does not treat immunity and other targeted-switch interactions exhaustively.
It assumes input predicates already account for the card's actual
legality, public board, and preventing effects. Delayed effects from
Abilities triggered by movement also need a richer event model.
