# Search observation bridge: preserving information-only search value

## Question

What should a planner do when a legal constrained deck search produces no useful material target but still inspects the full deck?

It should preserve the observation as a separate state transition.

The existing typed Trainer search allocator intentionally emits only useful nonzero material outputs. That is correct for material connector feasibility. The search-legality result shows a different dimension: a nonempty constrained search can legally execute with zero eligible targets and still reveal the deck.

This bridge keeps those two projections separate.

Implementation: `tools/search_information_bridge.py`

Reproducer: `results/search_information_bridge/reproduce.py`

## Representation

`SearchInformationProjection` records:

- whether a full-deck observation was applied;
- whether a material action is available in the companion planner;
- the prior Prize belief;
- the posterior Prize belief.

`project_search_information()` consumes an already resolved `SearchResolution`. It does not try to decide card legality again.

If `inspected_full_deck` is true, it replaces the grouped Prize belief with the exactly observed composition. If the search never reached deck inspection, the prior belief is preserved.

This keeps one authoritative ordering:

`legality -> search execution -> observation -> material movement`

## Targetless search witness

The regression starts from the exact grouped hypergeometric prior used by the Prize-belief work for two singleton strategic groups A and B in a 53-card unknown population with six Prizes.

A constrained Item search resolves with:

- 40 cards in deck;
- zero eligible material targets;
- full deck inspection reached.

The companion material projection is deliberately marked unavailable.

The information projection still occurs. Prior entropy is positive and posterior entropy becomes zero after supplying the observed Prize composition.

This is the state shape a material-only connector graph cannot represent if it deletes every zero-output search edge.

## Blocked destination witness

The regression also uses a direct-to-Bench Item search with zero open Bench slots.

The search action is blocked before deck inspection. The bridge therefore preserves the prior belief and emits no observation.

This prevents the opposite planner error: granting Prize information merely because the card text contains a search phrase.

## Quantified strategic consequence

For two equal alternative lines, each requiring one different singleton to be unprized, the repository's exact Prize-information model gives:

- best fixed pre-information line: 88.679245283%;
- adaptive post-information choice: 98.911465893%;
- value of exact Prize information: 10.232220610 percentage points.

The targetless search witness receives that information value when the observation occurs before the modeled commitment.

The full-Bench blocked search receives zero because deck inspection never occurred.

The number is a decision-model result rather than a universal card value. It assumes the line choice remains available after the search and ignores other costs of taking the action.

## Architectural consequence

Material reachability and observation reachability should be sibling outputs of a resolved action.

A planner can therefore encounter all three useful combinations:

| Material output | Observation | Meaning |
| --- | --- | --- |
| yes | yes | ordinary productive full-deck search |
| no | yes | legal targetless search with information value |
| no | no | blocked or otherwise non-inspecting search branch |

This avoids forcing the material allocator to emit artificial zero-output connectors solely to preserve information.

## Validation

The reproducer asserts:

- a targetless nonempty constrained Item search applies exact Prize observation while `material_action_available=False`;
- a full-Bench direct-to-Bench Item preserves the prior belief;
- an ordinary target-moving search can expose both material and observation outputs;
- the two-singleton precommitment VPI equals `0.10232220609579101` when observation executes;
- the blocked search contributes zero VPI under the same decision timing.

## Limitations

The bridge consumes a resolved search event. It does not parse arbitrary card text or duplicate the legality engine.

The exact posterior requires the realized grouped Prize composition supplied by the game state. In an actual simulator that composition comes from the physical hidden state once full deck inspection makes it inferable to the player.

The VPI helper applies only when the observation arrives before the modeled line commitment. Supporter, attack, Bench, discard, and other timing costs can reduce the strategic value in a full turn model.

## Next useful work

The next integration should expose observation events from compiled search transactions at their exact resolution point, then feed them into the canonical turn state alongside material zone changes.

That would let the planner retain information-only branches without weakening the material allocator's current requirement that every emitted connector action contribute useful material output.
