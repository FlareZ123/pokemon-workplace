# Effect-order authority is part of timing state

## Question

Can one global "who chooses the order" rule cover simultaneous Pokémon TCG
effects, including Knock Out redirections?

Implementation: `tools/effect_order_authority.py`  
Regression: `results/effect_order_authority/reproduce.py`

## Evidence

The bundled Advanced Player's Rulebook v3.4 assigns different choosers at
different timing boundaries:

| Timing case | Ordering authority |
| --- | --- |
| several effects activate when one Pokémon is damaged | player of the Pokémon taking the damage |
| several Pokémon are Knocked Out at the same time and activate several KO-step effects | player whose turn is currently being played |
| several effects activate when Energy is attached | player whose turn is currently being played |
| several effects apply during Pokémon Checkup | player whose turn would be next |
| several end-of-turn effects apply | player whose turn is ending |

The current rulebook wording is intentionally preserved as separate cases rather
than normalized to one "active player" concept.

An official Pokémon Asia Trainers Website ruling provides a narrower
single-Pokémon Knock Out case:

https://asia.pokemon-card.com/ph/rules/search/?keyword=Lost+City

If Reuniclus with Persistent Cells is Knocked Out while Lost City is in play,
Reuniclus's owner chooses whether Persistent Cells or Lost City resolves first.
That choice determines whether the evolved Pokémon goes to hand or the Lost
Zone.

This card-specific ruling and the v3.4 several-Pokémon KO rule can coexist:
they have different trigger topology.

## Representation

`OrderAuthorityCase` contains only evidence-backed scopes currently used by the
research:

- damaged-Pokémon trigger group;
- multi-Pokémon simultaneous KO trigger group;
- Energy-attachment trigger group;
- Pokémon Checkup effect group;
- end-of-turn effect group;
- the specific Lost City + Persistent Cells ruling.

`OrderAuthorityContext` stores the roles needed by those rules:

- current-turn player;
- next-turn player;
- affected Pokémon's player, where relevant;
- Knocked Out Pokémon owner, for the specific official ruling.

`ordering_player()` returns a chooser only when the relevant role is supplied.
It does not infer missing ownership.

## Regression

The regression deliberately puts Player A on turn while the affected and
Knocked Out Pokémon belongs to Player B.

The resulting chooser changes by timing:

- damaged-Pokémon effects: B;
- multi-Pokémon KO effects: A;
- Energy-attachment effects: A;
- Pokémon Checkup: B;
- end of turn: A;
- Lost City + Persistent Cells: B.

The test therefore falsifies either player as a universal chooser.

## Finding

Effect-order authority is a state variable tied to timing and trigger topology.

A simulator should keep at least these layers separate:

1. which effects are simultaneously eligible;
2. which rule or ruling determines the player with ordering authority;
3. the order that player chooses;
4. physical execution of effects in that order.

Collapsing those layers into a generic "current-turn player orders simultaneous
effects" rule creates a concrete wrong result for the official Lost
City/Reuniclus case.

## Scope and limits

The catalog is deliberately incomplete. The specific Reuniclus owner-choice
ruling is not generalized to every single-Pokémon Knock Out conflict without
additional authoritative evidence.

Likewise, the multi-Pokémon KO entry follows the exact v3.4 condition: several
Pokémon are Knocked Out at the same time and activate several effects in KO
step 2.

Future timing families should be added only with explicit rules or rulings.
