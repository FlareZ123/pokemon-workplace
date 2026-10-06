# Bench capacity geometry: slack, peak occupancy, and forced contraction

## Question

How should Expanded research represent Bench space when search routes, one-shot support Pokémon, and Bench-capacity effects interact?

## Answer

Bench space is a state resource with a hard capacity. A line can be legal at its starting and ending board sizes while still being impossible because its temporary peak occupancy exceeds the current capacity. Capacity can also change during a game, which can force the affected player to discard Benched Pokémon. Those forced discards can remove strategically valuable pieces or clean up spent liabilities, depending on the board.

This result adds two reusable tools:

- `tools/bench_resource_catalog.py` extracts current paper Expanded Bench-capacity effects, hand-to-Bench Ability triggers, and Trainer-based Bench cleanup resources from the bundled card pool while respecting the repository legality overlay.
- `tools/bench_capacity_model.py` formalizes effective capacity, route peak occupancy, and the affected player's optimal discard choice after a forced contraction.

`results/bench_capacity_geometry/reproduce.py` checks the key catalog and model properties.

## Rules basis

The Advanced Player's Rulebook states that a player can normally have at most five Pokémon on the Bench and can play Basic Pokémon onto the Bench one at a time. It also states that a Trainer card or Ability that would put a Pokémon onto the Bench cannot be used when the Bench is full. Card text takes priority when it changes the basic rules.

These rules justify treating Bench slack as a hard action constraint.

## Computational card-pool findings

The catalog uses the repository's paper Expanded legality baseline, including the official-ban overlay already maintained by `tools/build_expanded_legality_baseline.py`.

In the bundled snapshot, the catalog finds 17 legal print records corresponding to seven normalized Bench-capacity text variants:

| Card | Capacity | Affected side | Important condition |
| --- | ---: | --- | --- |
| Sky Field | 8 | both | Stadium in play |
| Area Zero Underdepths | 8 | both | each affected player needs a Tera Pokémon in play |
| Eternatus VMAX | 8 | self | all of your Pokémon in play must be Darkness type |
| Collapsed Stadium | 4 | both | Stadium in play |
| Sudowoodo, Roadblock | 4 | opponent | Ability active |
| Parallel City | 3 | chosen side | orientation selected when Stadium is played |
| Glimmora ex, Dust Field | 3 | opponent | Glimmora ex must be Active |

The same pass finds 124 legal print records whose Ability text triggers when that Pokémon is played from the hand onto the Bench, representing 51 exact normalized text variants. A deliberately conservative text heuristic marks 19 of those variants as resource-access effects. Nine of the 19 carry a two-Prize rule. Examples include Tapu Lele-GX, Dedenne-GX, Crobat V, Jirachi-EX, Hoopa-EX, Eldegoss V, Lumineon V, and Meowth ex.

The resource-access classifier is a discovery heuristic. It is not a complete semantic parser, so the count should be interpreted as a reproducible lower-resolution catalog rather than a definitive taxonomy of every strategically useful Bench trigger.

The Trainer cleanup scan finds AZ, Acerola, Cassius, Giovanni's Exile, Professor Turo's Scenario, Scoop Up Cyclone, Super Scoop Up, and Volo among the current legal candidates captured by its patterns. Scoop Up Net is excluded because the legality layer marks its Expanded prints banned. Several cleanup lines consume the Supporter window, have targeting restrictions, use the ACE SPEC slot, or depend on a coin flip.

## Mathematical model

Let:

- `C` be the current effective Bench capacity;
- `B` be the current number of Benched Pokémon;
- `S = C - B` be Bench slack;
- `d_i` be the Bench-occupancy change caused by step `i` of a proposed line.

For a line whose relevant capacity stays fixed, define its temporary peak increment as:

`P = max(0, d_1, d_1 + d_2, ..., d_1 + ... + d_n)`.

The line is Bench-feasible exactly when:

`B + P <= C`.

This condition depends on the largest prefix occupancy. Final occupancy alone cannot establish feasibility.

Example: starting at four occupied slots under the normal capacity of five, a line with Bench deltas `(+1, +1, -1)` ends at five. Its intermediate peak is six, so it fails before the cleanup step can happen. Under an active eight-slot expansion, the same occupancy sequence is Bench-feasible.

### Effective capacity

The current cards explicitly instruct players to use the smaller number when several effects change the allowed number of Benched Pokémon. The model therefore treats eight-slot effects as expansions above the default five and applies active restrictions afterward.

Examples:

- default: `5`;
- Sky Field alone: `8`;
- Sky Field plus Sudowoodo affecting that player: `4`;
- Area Zero Underdepths plus Collapsed Stadium: `4`;
- Sky Field plus the restricting side of Parallel City: `3`.

## Bench debt

A one-shot utility Pokémon can create immediate value when it enters play and then continue occupying a Bench slot after its entry Ability has resolved. The occupied slot is a persistent state cost until some later action removes, promotes, Knocks Out, or otherwise changes that Pokémon.

This result calls that persistent cost **Bench debt**. Bench debt is state-dependent. A support Pokémon can later become a useful attacker, pivot, evolution target, sacrifice target, or other resource, so its continuation value can increase again.

Two-Prize support Pokémon can have especially low continuation value after their entry effect is spent because they also create a possible Prize route for gust effects. That statement is a strategic heuristic whose magnitude depends on matchup and board state.

## Forced contraction as a choice problem

Suppose a capacity effect disappears or a restriction enters play and the affected player must shrink from occupancy `B` to capacity `C'`. The number of forced discards is

`D = max(0, B - C')`.

Assign each current Bench occupant a state-relative continuation value `v_j` to the affected player. Under card texts where that affected player chooses which Pokémon to discard, the immediate value loss from contraction is minimized by discarding the `D` occupants with the smallest continuation values.

If the sorted values are `v_(1) <= v_(2) <= ...`, the stylized immediate loss is

`L = v_(1) + ... + v_(D)`.

This yields an important strategic consequence: a Bench restriction can clean up spent utility Pokémon for the opponent. If one or more stale occupants have zero or negative continuation value, the first forced discards may impose little cost or may even improve the affected player's board. A constricting effect therefore cannot be scored as a fixed positive disruption value independent of board composition.

The same logic makes the loss of an eight-slot expansion dangerous when the expanded Bench contains several live pieces. A board at eight that contracts to five must discard three occupants, so three stale occupants are required to absorb the contraction without discarding a live piece in this simplified model.

## Relationship to existing typed-access work

`tools/typed_access_network.py` already models a static `bench_count` and `bench_limit` and correctly removes the Tapu Lele-GX connector line when the Bench is full. The present result identifies two extensions needed for broader simulations:

1. capacity should be derived from active Stadiums, Abilities, and conditions rather than assumed to stay at five;
2. a route evaluator should inspect temporary peak occupancy and forced-contraction choices, not only the occupancy of a single state.

This connects Bench geometry to Active Move Realism and connector domination. A search path can exist in a card-association graph while being mechanically unavailable because it needs more temporary Bench slack than the state provides. A route can also consume a scarce slot that a stronger competing route needs later.

## Validation

`reproduce.py` asserts that:

- the seven expected capacity effects are present and their caps and targets match the extracted card text;
- Scoop Up Net is absent from the legal cleanup catalog;
- several important entry-trigger support Pokémon are present;
- expansions and restrictions combine to the smaller applicable cap;
- a `(+1, +1, -1)` line from occupancy four fails at capacity five despite ending at five;
- the same line succeeds at capacity eight;
- forced contraction selects the lowest modeled continuation-value occupants first.

The mathematical functions are deterministic. The card catalog is deterministic for a fixed bundled database and legality overlay.

## Limitations

The catalog is targeted infrastructure rather than a general card-text parser. It can miss semantically equivalent effects with unfamiliar wording. The cleanup scan focuses on Trainer text and does not claim to enumerate every Pokémon attack or Ability that can remove a Bench occupant.

The continuation-value contraction model is deliberately local. It omits future draw, Prize mapping, opponent gust access, damage, attached resources, Active-position requirements, turn windows, and the opportunity cost of the Stadium or Supporter used to change Bench capacity. Those variables belong in a fuller state model.

The capacity formula also assumes the currently extracted eight-slot expansions and three/four-slot restrictions. Any future card with a different interaction may require a richer rule-resolution representation.

## Next useful work

The highest-value extension is to connect this Bench kernel to the typed access engine and to deck-specific setup models. That would allow exact or simulated estimates of how often a connector line is blocked by temporary Bench peak, how often a support Pokémon becomes stale Bench debt, and how much a capacity contraction helps or hurts in realistic board states.
