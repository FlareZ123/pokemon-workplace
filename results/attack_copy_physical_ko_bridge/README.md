# Copied attack damage into a physical Knock Out batch

## Question

Can copied-attack damage move directly from an executable copy trace into the
repository's stack-bearing physical-card state and simultaneous Knock Out
machinery?

Yes for the modeled damage/effect-counter subset.

Implementation: `tools/attack_copy_physical_ko_bridge.py`  
Regression: `results/attack_copy_physical_ko_bridge/reproduce.py`

## Motivation

The first copied-attack damage bridge used `board_object_kernel.py`, while the
physical conservation and simultaneous Knock Out work uses the richer
`board_position_state.py` plus `StackBoardMaterialState`.

That split leaves an integration gap. A planner can know which lightweight board
objects reached zero HP without yet having the evolution stacks, attachments,
and physical card instances needed for a correct Knock Out trigger/disposal
phase.

This result replays the copy event stream directly on the stack-bearing board.

## Representation

`PhysicalBoardEventProgram` supplies one board consequence for an ordered copy
event:

- normal damage target and `DamageContext`;
- effect-based damage-counter placements.

`replay_copy_attack_physical_board()` applies those transitions to the
`BoardPokemon.damage_counters` fields while leaving the identity ledger
unchanged and validated after each state change.

The replay returns:

- the updated `StackBoardMaterialState`;
- ordered damage results;
- effect-counter outcomes;
- event snapshots;
- the final same-board Knock Out candidate IDs.

No card instance is created, removed, or moved merely because damage changed.

After all applicable post-damage reactions have been resolved,
`prepare_physical_knockouts()` enters the existing
`PendingKnockOutBatch` phase without converting board representations.

## Phantom Dive witness

The regression uses Haughty Order -> Phantom Dive against a physical board with:

- a 200 HP Active carrying a Tool;
- a 60 HP Benched Pokémon carrying a Basic Energy;
- a surviving third Pokémon.

Every Pokémon card and attachment has a materialized physical instance in the
identity ledger.

The copied attack records:

`reveal top 10 -> Phantom Dive body -> shuffle revealed cards`

The Phantom Dive body places:

- 200 normal damage on the Active;
- six effect counters on the 60 HP Bench target.

The outer shuffle continuation remains last in the event trace. After that
continuation, the bridge reports both targets as Knock Out candidates.

## Physical KO handoff

Preparing the KO batch does not remove either doomed Pokémon.

The pending state still contains:

- the zero-HP Active;
- the zero-HP Bench target;
- the Tool attached to the Active;
- the Energy attached to the Bench target;
- the surviving third Pokémon.

That is the required trigger window.

The regression then calls the existing atomic batch-disposal transition and
promotes the survivor. The two Pokémon cards, Tool, and Energy all enter their
exchangeable discard counts, while the surviving Pokémon remains materialized
in play.

Per-card-class totals are invariant from the initial hand state through damage,
pending KO, disposal, and promotion.

## Finding

Damage state and physical-card conservation can share one board authority.

For this subset, the executable path is now:

`copy event stream -> stack-bearing damage state -> final KO IDs -> pending physical KO batch -> atomic disposal/promotion`

This removes one representation jump between attack execution and Knock Out
conservation.

It also preserves the earlier phase barrier. The pending batch is still a
separate state and must finish before any turn-boundary directive from a copied
body is consumed.

## Limits

The bridge currently supports normal damage and effect-based counter placement.
It does not compile those semantics from card text.

The test has no damaged-by-attack reaction. If such reactions are applicable,
they must be resolved before `prepare_physical_knockouts()`, because they can
add Knock Outs on either side.

The current physical bridge is one-board. Cross-player simultaneous KO grouping,
trigger routing, Prize taking, promotion order, and game resolution remain in
the repository's downstream Knock Out infrastructure.
