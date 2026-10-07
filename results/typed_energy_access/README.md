# Typed Energy access: zone reachability and attack readiness in one state search

## Question

Can a state-transition model follow the Iron Thorns ex setup line from search cards through Energy attachment and verify that the final board actually pays Volt Cyclone?

Yes.

This result adds `tools/typed_energy_access.py`, a small breadth-first state search that composes the repository's typed zone/action approach with `tools/energy_action_budget.py`. The engine keeps card zones and action budgets explicit, then calls the Energy solver to test the attack-ready goal.

The modeled line is:

`Tag Call -> Guzma & Hala -> Double Colorless Energy + Thunder Mountain Prism Star -> Volt Cyclone ready`

The human prior-research document identifies this as an Archetype-Line-Specific interaction for Iron Thorns ex. The current result turns the decisive segment into an executable state transition model.

## Why integration changes the question

A card graph can show that Tag Call reaches Guzma & Hala, that Guzma & Hala reaches Double Colorless Energy and Thunder Mountain, and that those cards relate to Iron Thorns ex. That is insufficient to establish a turn.

The integrated state search asks, in order:

1. Is the connector in a zone where it can legally be used?
2. Does its action class remain available?
3. Are optional costs such as the two-card Guzma & Hala discard payable?
4. Do the searched cards enter the correct zones?
5. Can the Stadium still be played?
6. Is the normal Energy attachment still unused?
7. After those transitions, do the attached Energy units and active cost reductions satisfy Volt Cyclone's typed `LCC` cost?

This separates search reachability from attack readiness while keeping both in one executable line.

## State representation

`EnergyAccessState` currently preserves:

- tracked card locations: deck, hand, discard, play, Active, or attached;
- whether the Supporter action has been used;
- whether a Stadium has been played;
- whether the normal Energy attachment has been used;
- whether Thunder Mountain Prism Star is active;
- Energy units currently attached to the attacker;
- whether Items, Supporters, Stadium plays, normal attachments, and attacks are available in the represented state.

The card-specific transitions are deliberately small and auditable:

- Tag Call moves Guzma & Hala from deck to hand;
- Guzma & Hala searches Thunder Mountain Prism Star and, after the optional two-card discard, Double Colorless Energy;
- Thunder Mountain moves from hand to play and activates the Lightning cost reduction;
- Double Colorless Energy moves from hand to the attacker through the one normal attachment and contributes two Colorless Energy units.

`volt_cyclone_ready()` converts the resulting board summary into the exact Energy solver. It requires the target to be Iron Thorns ex in the Active Spot and attacks to be available.

## Baseline result

From the represented zero-Energy start with Tag Call in hand, Guzma & Hala, DCE, and Thunder Mountain in deck, plus two discardable hand cards, breadth-first search finds this shortest four-action line:

1. `Tag Call -> Guzma & Hala to hand`
2. `Play Guzma & Hala; discard 2 -> Thunder Mountain + DCE to hand`
3. play Thunder Mountain Prism Star and attach Double Colorless Energy, in either order
4. perform the other of those two actions

After both final setup actions, the Energy layer sees Volt Cyclone's `LCC` demand, removes the `L` requirement through Thunder Mountain, and pays the remaining `CC` with the two units from DCE.

The BFS therefore establishes the complete represented path from initial card zones to an attack-payable state.

## Constraint regressions

The reproducer verifies several ways the same card-association graph can remain visually connected while the actual line disappears.

| State change | Result | Failure point |
| --- | --- | --- |
| Remove one discardable hand card | no line | Guzma & Hala cannot take its optional Special Energy search branch |
| Disable Items | no line | Tag Call transition disappears |
| Disable Supporters | no line | Guzma & Hala transition disappears |
| Disable Stadium play | no line | Lightning cost remains unpaid |
| Mark the normal attachment as already used | no line | DCE cannot move from hand to the attacker |
| Disable attacks | no attack-ready goal | board construction cannot satisfy the modeled goal while the attack is unavailable |

These failures occur at different semantic layers. A single scalar such as access count, consistency score, or total Energy availability cannot explain all of them.

## Existing attachment changes the line

A second regression starts with Double Colorless Energy already attached to Iron Thorns ex and the normal attachment already spent.

DCE alone does not satisfy `LCC`. The BFS only needs three further actions:

1. Tag Call for Guzma & Hala;
2. Guzma & Hala for Thunder Mountain;
3. play Thunder Mountain.

The Energy solver then confirms the attack is payable.

This is useful because the same desired attack can have different shortest setup lines depending on persistent Energy state inherited from earlier turns.

## Card-pool anchors

`results/typed_energy_access/reproduce.py` loads the bundled card database and confirms Expanded-legal records for the exact prints used by the model:

- Tag Call `sm12-206`;
- Guzma & Hala `sm12-193`;
- Double Colorless Energy `sm2-166`;
- Thunder Mountain Prism Star `sm8-191`;
- Iron Thorns ex `sv6-77`.

It asserts the relevant search text, discard condition, Energy-provision text, Stadium cost reduction, and Volt Cyclone cost before running the state-search regressions.

## Relationship to existing repository models

`tools/typed_access_network.py` established that zone transitions and action windows matter for Supporter access. `tools/energy_action_budget.py` established that Energy supply, typed demand, reductions, restrictions, and resource budgets need separate semantics.

The current result is a first composition of those ideas. The state engine discovers a card sequence. The Energy kernel judges the final attack-payment condition.

That decomposition suggests a larger simulator architecture:

- typed state transitions govern zones, locks, triggers, and action timing;
- resource allocators govern shared finite budgets;
- an Energy kernel governs attack-cost satisfaction;
- strategic policy evaluates whether a mechanically valid line is worth taking.

## Limitations

This is still a research scaffold. It hard-codes one archetype line and a few card actions. It does not parse arbitrary card text. It also does not yet model Prize states, deck stochasticity, opponent interaction, turn ownership, Bench targeting after Volt Cyclone, retreat, Energy discard, competing attackers, or existing Stadium replacement rules in full detail.

The `stadiums_allowed` flag is an abstract state gate for experiments. It should not be read as claiming a universal Pokémon TCG rule that Stadium cards share the same lock semantics as Items or Supporters.

The result establishes a representation and a verified example rather than a complete game engine.

## Next useful work

The strongest extension is to generalize the transition compiler so card actions emit typed state changes and Energy effects without being hard-coded to one archetype. Crispin is a useful next case because one Supporter action simultaneously searches two Basic Energy cards, attaches one by effect, and places the other in hand where it can use the independent normal attachment.

A second extension is turn-window semantics. That would let the same engine distinguish a legal going-second attack line from a line whose required Supporter or attack is unavailable in the current turn state.
