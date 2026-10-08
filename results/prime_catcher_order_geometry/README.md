# Prime Catcher creates a nonmonotonic own-Bench sequencing constraint

## Question

Prime Catcher is commonly represented in tactical models as an unrestricted
opponent gust attached to an ACE SPEC Item. Its printed effect also switches
your own Active with a Benched Pokemon **after** the opponent's switch resolves.
Can adding a seemingly harmless support Pokemon to your own Bench make the
same gust attack turn impossible?

Yes, in a precisely stated same-turn attack-readiness model.

## Source text and rules

Official English card text, [Prime Catcher — Temporal Forces 157](https://asia.pokemon-card.com/sg/card-search/detail/12247/):

> Switch in 1 of your opponent's Benched Pokemon to the Active Spot.
> If you do, switch your Active Pokemon with 1 of your Benched Pokemon.

The bundled Advanced Player's Rulebook clarifies switching by an Item is
different from retreating, and II-A / E-20 gives conditional multi-step
execution rules. The opponent's targeted switch happens **first**. If it
succeeds, the player must perform their own switch when that is possible.
If the player has **no Benched Pokemon**, that second part cannot happen;
the successful opponent switch remains. The own switch cannot be voluntarily
skipped when a legal own Benched Pokemon is present.

Other important boundary: when no eligible opponent Benched Pokemon can be
switched, the opponent-targeted first action cannot succeed, so the own
switch is not performed under the card's `If you do` wording. The
experiment conditions on at least one legal opposing Bench target.

These distinctions also matter for Cross Switcher, which has a similar
opponent-first then own-switch structure but requires two card copies
simultaneously.

## Executable one-turn model

The opponent has a legal Benched target that can be Knocked Out by a
**ready** attacker this turn after being gusted. The player has exactly
one Prime Catcher in hand and an own Active Pokemon that is either ready or
unready to perform that KO. The own Bench contains zero through five Pokemon,
each tagged ready or unready for this narrow KO endpoint.

A *ready* label is an external predicate incorporating all actual HP, Energy,
attack legality and other requirements. The model does not infer it from
card names.

Before attacking, the player can:

1. Bench any represented Basic Pokemon from hand (up to five total).
2. Play Prime Catcher and target the opponent's Bench. If the player has
   at least one own Benched Pokemon, choose one to switch with the Active.
3. Optionally use one additional, already executable **Switch-like**
   self-switch, which may be played before or after Prime Catcher.

A successful endpoint requires the opponent target to be gusted, the own
Active to be ready for the required KO, and any represented mandatory
hand-to-Bench setup to be complete before the attack.

`tools/prime_catcher_order_geometry.py` enumerates actual legal action
sequences. A breadth-first search returns a shortest witness, including
the fact that a prior extra self-switch can set up the desired own target.

## The empty-Bench paradox

Assume the current Active is ready and there is **no additional Switch**.

| Own Bench before Prime | Own attack ready after Prime? | Why |
| --- | --- | --- |
| Empty | **Yes** | Opponent target is gusted; impossible own switch is ignored |
| One unready Pokemon | **No** | Mandatory own switch promotes the unready Pokemon |
| One ready Pokemon | **Yes** | Mandatory switch promotes a ready attacker |
| Any number of Pokemon, at least one ready | **Yes** | Choose a ready Benched attacker |
| One or more Pokemon, all unready | **No** | Every permitted promotion loses attack readiness |

More own Bench occupancy can therefore *reduce* the immediate usability
of this ACE SPEC, even though each extra Pokemon is itself a legal Bench
addition.

With an extra executable Switch, the player can restore the original
ready attacker after Prime, or first switch an unready Pokemon Active and
then use Prime to move the original attacker back Active.

## Exact finite-geometry census

There are 63 Boolean Bench-readiness profiles across occupancy 0..5:

`1 + 2 + 4 + 8 + 16 + 32 = 63`

With the own Active initially **ready** and no additional Switch:
**58/63** profiles can still gust and attack after Prime. The five failures
are exactly the all-unready Bench at each nonzero occupancy 1..5.

Adding one independent self-switch raises feasibility to **63/63**.
With the own Active initially **unready**, Prime alone enables the
gust-and-attack endpoint in **57/63** profiles, precisely those with at
least one ready Pokemon already on the Bench.

These are exact Boolean geometry counts, not estimates of hand, deck or
matchup probabilities.

## Sequencing witness: a Basic is available in hand

Start with a ready Active, **no own Bench**, one unready Basic Pokemon in
hand, Prime Catcher accessible, and no extra Switch. The Basic must be
Benched by the attack deadline.

- **Prime first, then Bench:** Prime gusts the opponent, finds no own
  Bench target to move, and leaves the current attacker ready. The unready
  Basic is Benched afterward. **Endpoint succeeds.**
- **Bench first, then Prime:** the unready Basic becomes the only possible
  own-switch target. Prime must promote it, leaving the current attacker
  on the Bench and unable to perform the desired KO that turn. **Endpoint
  fails** without another switch resource.

The board after both actions can contain the same two own Pokemon while
the ordering alone determines whether the immediate attack is available.

Across all 31 opening own-Bench-readiness profiles with 0..4 occupants
and one additional Basic that **must be Benched**, an unready Basic gives
27 reachable endpoints and four failures without Switch. Replacing that
Basic with a ready attacker gives **31/31** reachable endpoints; keeping
it unready but adding one Switch also gives **31/31**.

## Validation

- `tools/prime_catcher_order_geometry.py`: exact action transitions and
  breadth-first winning-sequence search.
- `results/prime_catcher_order_geometry/reproduce.py`: independently
  coded depth-first reachability oracle.
- **376 state combinations** cross-validated, including own Active ready
  or unready, all 0..5 own-Bench readiness patterns, a zero/one additional
  Switch budget, and forced-Bench-from-hand cases.
- Specific assertions cover empty own Bench, mandatory own switch, extra
  Switch recovery, ready-Bench promotion, and opposite outcomes for
  Prime-before-Bench versus Bench-before-Prime.

## Consequences and limits

An access graph that treats Prime Catcher as simply a deterministic
opponent gust loses important own-board constraints. Its real tactical
value depends on *which Pokemon is Active afterward*, and sometimes on
whether the player delays a seemingly harmless Basic Bench placement.

The model abstracts every actual attack cost as a readiness Boolean. It
omits the player's normal retreat, other switching abilities, attack
restrictions that disappear upon switching, Ability-triggered events,
locks, cards needed to obtain Prime, and Prize effects of the KO. Such
interactions can either recover or improve a Prime line in real play.

Future work should couple this action-order kernel to the shared typed
Bench and Energy state, using exact current attack readiness and cards
available before the target KO.
