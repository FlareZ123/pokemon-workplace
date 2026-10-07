# Unified mechanical-state kernel

## Question

Can the repository's separate typed treatments of zones, Bench capacity, lock channels, Energy readiness, and Prize uncertainty share one deterministic state without duplicating or contradicting one another?

This result provides a first composition layer.

Implementation: `tools/unified_state_kernel.py`  
Regression: `results/unified_state_kernel/reproduce.py`

## Scope

The kernel is intentionally a narrow research scaffold rather than a full rules engine. It composes existing lower-level repository components:

- `bench_state_kernel.py` for Bench residents and capacity contraction;
- `lock_state_kernel.py` for typed play permissions and Tool attachment/effect state;
- `energy_action_budget.py` for exact typed attack-cost satisfaction;
- `prize_belief_kernel.py` for grouped Prize-composition uncertainty.

The unified layer owns one canonical card-zone map. Subsystems carry only the state they specialize in. This matters because separate zone maps for access, Bench, Energy, and Prize logic can silently disagree about where one physical card is.

## State boundary

`UnifiedState` currently carries:

- canonical card locations;
- `BenchState`;
- `PlayerChannels`;
- Active Pokémon identity and `PokemonState`;
- Active Tool identity, when modeled;
- Active target tags;
- Ability availability;
- normal Energy-attachment usage;
- Stadium usage;
- physical attached-Energy cards, with a legacy unit-only fallback for older callers;
- attack-cost reductions;
- attack availability;
- whether Gladion has been played in the represented line.

Cross-kernel validation checks that every modeled Bench resident is actually in the Bench zone and that the named Active Pokémon is actually in the Active zone.

The representation is immutable and hashable, so the same object can be used directly in breadth-first search.

## Regression 1: one access line, four independent failure layers

The baseline current-turn line is:

`Quick Ball -> Tapu Lele-GX from hand -> Wonder Tag -> Gladion`

with one discardable card in hand and both Tapu Lele-GX and Gladion in the deck.

The planner finds:

1. `Quick Ball -> Tapu Lele-GX to hand`
2. `Play Tapu Lele-GX from hand; Wonder Tag -> Gladion`
3. `Play Gladion`

The same nominal card-association path becomes unreachable if any of the following are changed independently:

- Item play is locked;
- Supporter play is locked;
- Abilities are unavailable;
- the Bench is full.

These failures are represented by different state channels. They do not collapse into one generic "access" boolean.

A Nest Ball route also fails even though it reaches the same Pokémon identity. Nest Ball puts Tapu Lele-GX directly onto the Bench, so the hand-play condition for Wonder Tag is not emitted.

## Regression 2: Item lock and Tool state remain distinct

The unified state reuses the lock kernel's separate Item and Tool channels.

Under Item lock:

- attaching Stealthy Hood to the Active Pokémon remains legal in the model;
- the Tool is represented as physically attached;
- its effect can later be suppressed without removing the attachment.

After Tool-effect suppression, the state therefore simultaneously records:

- `tool_attached = True`;
- `tool_effect_enabled = False`.

The composition layer also preserves the Tool's identity. This matters because the lower-level lock kernel intentionally uses a generic `tool_attached` bit for mechanics such as Garbotoxin. Without an identity field, a Choice Band attachment satisfies the same generic boolean as Stealthy Hood and can be misread as granting Stealthy Hood protection. The regression now attaches Choice Band and asserts that it does **not** protect the holder.

A broad Trainer lock removes the Tool-play transition entirely.

This is the compositional form of the asymmetry already established by the lock-state research.

## Regression 3: typed Energy endpoint in the same state

A second regression starts with Iron Thorns ex Active, Double Colorless Energy and Thunder Mountain Prism Star in hand, and the attack cost `LCC`.

The unified state applies two independent transitions:

1. attach Double Colorless Energy through the normal attachment, contributing two Colorless Energy units;
2. play Thunder Mountain, contributing one Lightning cost reduction because the Active target has the Lightning tag.

The attached DCE is now one physical Energy-card object that provides two Colorless units. The existing exact Energy solver receives a derived unit view and confirms the attack cost is satisfiable.

Either resource alone is insufficient.

The same physical state can then apply a generic two-Energy discard. The minimum-card transition discards the single DCE card, moves that physical card to the discard zone, removes both supplied units, and makes the `LCC` attack unpayable again despite Thunder Mountain remaining in play.

The same state also respects:

- Special Energy play denial;
- Stadium play denial;
- the once-per-turn manual attachment flag;
- attack availability.

This result overlaps deliberately with the concrete `iron_thorns_integrated_als` result at the Energy endpoint, while generalizing the state boundary to Bench, Tool, and Prize-belief composition.

## Regression 4: Bench contraction updates the canonical zone map

The Bench starts with four high-retention core residents and then accepts Tapu Lele-GX as a low-retention support resident.

When capacity contracts from five to four, the existing maximum-retention resolver discards Tapu Lele-GX.

The unified wrapper then changes the same physical card's canonical location from `bench` to `discard`.

This is small but important: a capacity solver that changes only an occupancy count while leaving the access layer believing the card is still on the Bench creates an inconsistent game state.

## Regression 5: exact Prize belief -> mechanical reachability

The unified layer includes a conservative adapter for strategically relevant singleton groups.

For the Quick Ball -> Tapu Lele-GX -> Gladion line, assume:

- Quick Ball and its discard card are already known in hand;
- Tapu Lele-GX and Gladion are two distinct singletons in a 53-card unknown pool;
- six cards are Prized uniformly from that pool.

The grouped Prize belief enumerates whether each singleton is Prized. For each belief state, the adapter moves the corresponding physical singleton from `deck` to `prize` and runs the same deterministic planner.

The line succeeds exactly when both singletons are unprized:

`P(success) = C(51, 6) / C(53, 6) = 0.7844702467343977`

or about **78.4470%**.

The reproducer independently checks the closed form against the belief-weighted planner.

The same belief combined with Item lock or a full Bench produces zero access probability. This demonstrates a useful composition rule:

> uncertainty should weight mechanically valid state transitions, rather than replacing mechanical validity with a probability score.

## Architectural implication

The repository's recurring "theoretical access is weaker than executable access" synthesis can be represented with a layered contract:

1. **belief layer**: what physical states might be true, and with what probability;
2. **canonical mechanical state**: where cards are and which persistent board facts hold;
3. **typed transition layer**: which actions are legal and how they mutate the state;
4. **resource solvers**: exact feasibility for specialized shared resources such as Energy;
5. **planner/policy layer**: search over transitions and evaluate strategic value.

This avoids forcing every subsystem into one giant monolithic object while still giving the planner one authoritative physical state.

## Validation

`reproduce.py` checks:

- the three-action baseline Gladion line;
- Item, Supporter, Ability, and full-Bench failure gates;
- direct-to-Bench failure of Wonder Tag;
- Tool attachment under Item lock;
- Tool identity preservation, including a non-Hood counterexample;
- Tool-effect suppression without detachment;
- Trainer-lock denial of Tool play;
- typed DCE + Thunder Mountain attack readiness from one physical DCE object;
- one-card DCE removal for a generic two-Energy discard, including synchronized zone and payment-state updates;
- Special Energy and Stadium play denial;
- turn-end denial for ordinary Item, Tool, manual Energy, and Stadium actions;
- Bench contraction plus zone synchronization;
- exact two-singleton Prize-belief weighting;
- exact known-unprized and known-Prized endpoint cases.

The baseline Prize-weighted result is asserted against the independent combinatorial expression `C(51,6) / C(53,6)`.

## Limits

The current kernel does not parse arbitrary card text.

The Prize adapter supports only one physical card per mapped group. Multi-copy groups need explicit identity-to-count allocation before they can be converted into deterministic zones safely.

The canonical location scaffold is also keyed by one unique string per modeled card. It cannot represent two gameplay-equivalent copies under the same key in different zones at once. [../multicopy_zone_state/](../multicopy_zone_state/) formalizes the stronger contract: keep exchangeable copies as per-zone counts, then materialize explicit object identity when topology or history differentiates them.

The Bench model still assumes unique modeled resident names. It does not yet attach per-Pokémon Energy, Tool, damage, evolution, or Ability state to every resident.

The Active representation is singular and does not yet support switching/retreat as first-class transitions.

Abilities are represented by one broad availability flag in the current scaffold. Target-specific Ability suppression needs a richer scope model.

Stadium replacement, normal turn progression, Prize taking, damage, Knock Outs, attack execution, setup, opponent state, and strategic utility are outside the current implementation.

The current scaffold still stores Supporter/turn-end state inside `BenchState`, manual attachment and Stadium usage on `UnifiedState`, and Retreat usage in the board-object layer. [../turn_action_budget/](../turn_action_budget/) now supplies a common immutable contract for migrating those duplicated per-turn resources into one canonical budget. Until that migration is complete, every ordinary unified action explicitly respects `BenchState.turn_ended`.

Physical Energy-card identity is now preserved for the represented Active attachment, but Energy ownership is still attached to the singular Active state. A larger engine must preserve those Energy objects when Pokémon move between Active and Bench.

## Next useful work

The strongest next extension is a **board-object identity layer** that stores per-Pokémon state for Active and Benched residents while the canonical zone map continues to own physical card location.

That would allow:

- switching and retreat without losing Energy or Tool state;
- Active-only lock sources to turn on and off as position changes;
- attack-applied temporary locks to clear on the correct position/evolution changes;
- Bench contraction to remove a full board object rather than only a resident record;
- Energy attachments and Tools to follow the correct Pokémon.

A second extension is a generic belief-to-state instantiator for multi-copy groups. It should preserve physical identity where required while allowing grouped Prize beliefs to remain compact.
