# Energy action budget: attack readiness needs typed supply, demand reduction, and action capacity

## Question

Does access to enough Energy-looking cards imply that an attack is realistically available this turn?

No.

For paper Expanded, attack readiness depends on at least four separable quantities:

1. the attack's remaining typed Energy demand;
2. the Energy units actually provided by attached cards;
3. demand reductions such as Thunder Mountain Prism Star;
4. finite action and state resources used to create that board, especially the normal once-per-turn manual Energy attachment.

This result adds `tools/energy_action_budget.py`, an exact deterministic evaluator for already-compiled Energy routes, plus `results/energy_action_budget/reproduce.py` with card-pool and regression checks.

## Rules basis

The local advanced manual states that a player may normally attach one Energy card from hand during their turn. It separately states that Energy attached by an effect is separate from that normal attachment. Those two rules make manual attachment bandwidth a state resource rather than a property of Energy access alone.

This immediately creates a distinction between:

- putting an Energy card into hand;
- manually attaching an Energy card;
- attaching Energy through an effect;
- moving already-attached Energy;
- reducing an attack cost;
- attaching one card that provides more than one Energy unit.

A realistic state model should preserve these as different transformations.

## Representation

An `EnergyRouteProfile` has four components:

- `units`: Energy units supplied to the attacker;
- `reductions`: exact attack-cost symbols removed;
- `resource_costs`: finite resources consumed, such as `manual_attachment`, `supporter_play`, `stadium_play`, discardable cards, Energy cards in hand, or donor Energy already in play;
- `required_target_tags`: restrictions such as `Lightning` or `Dragon`.

A route can represent one card action or a precompiled multi-card line. Physical route copies are allocated at most once each.

The evaluator reports three levels of feasibility:

| Level | Preserves Energy typing | Preserves target restrictions | Preserves finite resource budgets |
| --- | --- | --- | --- |
| Raw unit-count reachability | No | No | No |
| Typed resource-ignorant feasibility | Yes | Yes | No |
| Exact feasibility | Yes | Yes | Yes |

The exact solver uses dynamic programming over remaining attack-cost symbols and remaining resource capacities. Energy-unit assignment is enumerated exactly, so a unit can satisfy at most one symbol and Colorless requirements can be paid by any Energy unit.

## Core findings

### 1. Two Energy cards in hand can still be one turn short

Consider an attack costing `CC` with two ordinary Basic Energy cards available, zero Energy attached, and one normal attachment remaining this turn.

A count-only model sees two Energy units and declares the attack reachable. A typed model that ignores action capacity also declares it reachable. The exact model rejects the line because both cards require the same single manual-attachment resource.

This is a pure temporal-capacity failure. Nothing is missing from the hand except another attachment window.

### 2. One card can provide two Energy units

The bundled Expanded card pool contains legal Double Colorless Energy prints whose text says they provide two Colorless Energy.

For a `CC` attack, one Double Colorless Energy can therefore satisfy both symbols while consuming only one manual attachment.

This shows why `Energy card count`, `Energy units provided`, and `attachment actions consumed` cannot be represented by one scalar.

### 3. Energy quantity without type is insufficient

Double Colorless Energy contributes two units to a raw count. It still cannot satisfy an `RR` attack cost.

The reproducer verifies:

- raw unit-count reachability: yes;
- typed resource-ignorant feasibility: no;
- exact feasibility: no.

A converted-Energy-cost-only model therefore loses strategically necessary information.

### 4. Target restrictions are part of Energy semantics

Double Dragon Energy is legal in the bundled Expanded pool and provides two Energy units of every type while attached to a Dragon Pokémon, with an attachment restriction to Dragon Pokémon.

The exact model can satisfy an `RW` cost with one Double Dragon Energy on a Dragon target. The same route is rejected for a non-Dragon target even though a raw two-unit count still looks sufficient.

Target identity must therefore be part of Energy-route feasibility.

### 5. Cost reduction and Energy supply are different channels

Iron Thorns ex (`sv6-77`) has Volt Cyclone for `LCC`.

Thunder Mountain Prism Star reduces attacks of Lightning Pokémon by one Lightning Energy. With that Stadium active, Volt Cyclone's represented demand becomes `CC`. One Double Colorless Energy can then satisfy the remaining two symbols with one manual attachment.

The reproducer verifies this line exactly and rejects the Thunder Mountain reduction when the target lacks the `Lightning` tag.

This line is a concrete example of why demand reduction should not be encoded as if it were another attached Energy card.

## ALS case study: Guzma & Hala into Iron Thorns ex

The human prior-research document identifies a line in which Iron Thorns ex decks use Tag Call to reach Guzma & Hala, then use Guzma & Hala to obtain Double Colorless Energy and Thunder Mountain Prism Star. Thunder Mountain removes the Lightning requirement from Volt Cyclone, and Double Colorless Energy supplies the remaining two Colorless requirements.

The reproducer includes a **precompiled** version of the decisive Guzma & Hala segment. Its route signature is:

- supply: `CC` from Double Colorless Energy;
- demand reduction: remove one `L` from a Lightning target;
- consume one Supporter play;
- consume two discardable cards for Guzma & Hala's optional Special Energy search;
- consume one Stadium play;
- consume one manual Energy attachment.

With all four capacities available, the `LCC` demand is exactly satisfied. With only one discardable card, the compiled line is rejected even though its theoretical card graph remains connected.

This is an Energy-specific instance of Active Move Realism and connector domination. The search line is meaningful only when the downstream action budgets are payable.

The model deliberately starts after Tag Call has made Guzma & Hala accessible. Tag Call access, Prize states, locks, and the exact hand composition belong in a higher-level state-transition model.

## Effect attachment can coexist with the manual attachment

Crispin searches the deck for up to two Basic Energy cards of different types, puts one into hand, and attaches the other to a Pokémon.

The rules say an attachment produced by an effect is separate from the normal once-per-turn attachment. A legal compiled line can therefore use Crispin's effect attachment and then manually attach the Energy Crispin placed in hand, assuming the manual-attachment remains unused and all other requirements are satisfied.

The reproducer represents this as a two-unit precompiled route costing one Supporter play and one manual attachment. Removing the manual-attachment capacity makes the same two-Energy route fail.

This illustrates why a simulator needs to distinguish the attachment channel used by each Energy.

## Acceleration still has its own resource costs

Welder attaches up to two Fire Energy from hand to one Pokémon. The reproducer combines:

- a Welder route supplying `RR`, consuming one Supporter play and two Fire Energy cards in hand;
- one ordinary manual Fire attachment supplying the third `R`.

An `RRR` attack is feasible with three Fire Energy cards in hand, one Supporter play, and one manual attachment. With only two Fire Energy cards in hand, the typed resource-ignorant model says the route structure is sufficient while the exact model rejects it.

Acceleration bypasses the normal attachment count for the Energy attached by the effect. It does not bypass the need to possess the cards or pay the Supporter action.

## Moving Energy is not creating Energy

Energy Switch moves a Basic Energy already attached to one of your Pokémon to another Pokémon.

The model represents that as a supply route for the target that consumes a `donor_basic_energy` resource. With no donor Energy, the line fails. With one donor Energy, it succeeds for a one-symbol demand.

This matters for graph construction. An edge from Energy Switch to an attacker should not be counted as independent Energy production. It is a relocation edge whose feasibility depends on board state.

## Implications for deck and simulator design

A useful Energy representation should keep at least the following distinct:

- card access by zone;
- manual attachment capacity by turn;
- effect-based attachment capacity and its action class;
- attached Energy cards;
- Energy units each attached card currently provides;
- Energy types each unit can satisfy;
- target restrictions on an Energy card or effect;
- attack-cost reductions;
- Energy movement from existing donors;
- action resources such as Supporter plays, Stadium plays, discardable cards, Bench position, and locks.

This also clarifies how the repository's generic connector results should interact with Energy. Search connectivity can establish access to an Energy card while leaving attack readiness false. Resource-constrained connector allocation can track shared action budgets, while the Energy layer must additionally solve typed demand satisfaction and multi-unit provision.

The Energy evaluator now has a strict adapter from `TurnActionBudget` into its `supporter_play`, `stadium_play`, `manual_attachment`, and `retreat` resource keys. Supporter and Stadium play permission from `PlayerChannels` are applied separately. Existing explicit action-capacity keys are rejected when the adapter is used, preventing two state owners from silently supplying contradictory values.

The regression replays the compiled Iron Thorns/Guzma & Hala route from a fresh canonical budget and then rejects it when the relevant Supporter or Stadium channel is locked or the turn has ended. It also rejects a DCE attachment after the manual-attachment quota has already been spent.


## Validation

`results/energy_action_budget/reproduce.py` validates both the model and the local card records used as anchors.

It checks Expanded-legal records for:

- Iron Thorns ex (`sv6-77`);
- Double Colorless Energy (`sm2-166`);
- Thunder Mountain Prism Star (`sm8-191`);
- Double Dragon Energy (`xy6-97`);
- Welder (`sm10-189`);
- Energy Switch (`bw1-94`);
- Crispin (`sv7-133`);
- Guzma & Hala (`sm12-193`).

Regression cases cover manual-attachment contention, multi-unit Special Energy, typed mismatch, target restrictions, cost reduction, Supporter acceleration, Energy relocation, Crispin plus a normal attachment, and the compiled Guzma & Hala / Iron Thorns line.

The local reproducer passes all assertions.

## Limitations

This is an exact evaluator for **already-compiled deterministic routes**, not a full Pokémon TCG rules engine.

It does not yet model:

- card zones or search transitions directly;
- deck order or stochastic Energy hits such as Max Elixir;
- Prize cards;
- turn ownership or the first-turn Supporter restriction;
- Item, Ability, or Supporter lock as explicit state transitions;
- Energy discard after attacks;
- retreat;
- attacks that move Energy after damage;
- conditional Energy text beyond the target tags supplied to the route compiler;
- multiple attackers competing for the same Energy pool.

The Crispin and Guzma & Hala examples are intentionally precompiled lines. Their signatures are valid only when the higher-level prerequisites used to compile them are satisfied.

## Next useful work

The strongest next step is to integrate this Energy kernel with `tools/typed_access_network.py`.

The typed network can preserve zones, search actions, locks, Bench events, and Supporter windows. A compiled transition that attaches or moves Energy can then emit an Energy-route effect instead of being reduced to generic access.

That integration would let the repository distinguish three separate questions in one state model:

1. can the Energy card be reached;
2. can it be attached or moved before the deadline;
3. does the resulting typed Energy state actually satisfy the attack cost?

That would make ALS testing such as the Iron Thorns ex line substantially more faithful than an associativity graph alone.
