# Compiled Trainer searches can feed staged acquisition and execution planning

## Question

Can the staged objective planner receive search actions derived from existing conservative card-text compilers rather than hand-authored route summaries?

Yes, for fixed base search branches with known integer discard costs.

Implementation: `tools/compiled_search_staged_adapter.py`  
Regression: `results/compiled_search_staged_adapter/reproduce.py`

## Adapter boundary

The bridge consumes:

- a `CompiledTrainerSearchProfile`;
- the typed strategic demands used to validate the search;
- exact physical `SearchZoneTarget` groups;
- one validated `TypedTargetAction`.

It re-runs the typed target allocator to verify that the supplied action belongs to the compiled profile.

The exact target-cost vector is converted into physical card-class hand outputs. The compiled Trainer subtype becomes the staged action class, and the compiled mandatory discard count becomes the staged discard cost.

Conditional additional-search branches and whole-hand discard profiles are rejected for now because they need richer branch metadata than one fixed integer cost.

## Skyla and Secret Box

The regression obtains Skyla from the repository's single-output revealed-search compiler and Secret Box from the multi-output compiler.

For one searchable Boss's Orders:

- Skyla compiles into a Supporter acquisition action with zero discard cost;
- Secret Box compiles into an Item acquisition action with a three-card discard cost.

No route class or output card is hand-authored in this bridge.

## Objective-sensitive choice

With one ordinary Supporter use and three discardable cards, both compiled actions can acquire the singleton Boss's Orders.

For an acquisition-only objective, the staged planner chooses Skyla because it spends no discard.

For a same-turn Boss's Orders execution objective, the planner chooses Secret Box because the Item route preserves the Supporter window.

With two Supporter uses available, the same-turn objective switches back to Skyla.

This reproduces the earlier staged endpoint reversal using compiler-derived card semantics.

## Multi-output compilation survives the bridge

Secret Box is also compiled with exact Quick Ball and Boss's Orders targets.

The typed allocator selects the Item and Supporter axes from the four-axis card.

The adapter emits one staged action with:

- Boss's Orders x1;
- Quick Ball x1;
- discard cost 3;
- Item action class.

A staged objective requiring Quick Ball acquisition plus same-turn Boss's Orders execution completes both units with that single compiler-derived action.

## Architectural consequence

The local pipeline is now:

`card text -> conservative search profile -> typed physical target action -> staged acquisition action -> physical target depletion -> downstream execution scheduling`

This keeps target search semantics, discard costs, action-class contention, and execution deadlines traceable across layers.

## Limits

The adapter covers fixed base branches only.

It does not yet translate:

- Guzma & Hala-style optional paid branches;
- whole-hand discard effects;
- exact discard-card identity;
- arbitrary search destinations;
- random-gated search;
- full physical Trainer resolution.

Those should remain in their existing exact transaction layers until the adapter can carry equivalent witnesses.

## Next useful work

The next extension should expose validated branch metadata from the exact Trainer transaction layer, then adapt optional paid branches without duplicating branch-selection logic.
