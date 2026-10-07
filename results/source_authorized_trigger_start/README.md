# Source-authorized trigger scheduling

This result connects source-scoped ordering authority to the existing trigger-deferral scheduler.

Implementation:
- `tools/source_order_chooser.py`
- `tools/authorized_trigger_start.py`

Regression:
- `results/source_authorized_trigger_start/reproduce.py`

The concrete chooser helper maps abstract source claims to the actual current player, next player, or Knocked Out Pokémon owner. Selection from `TriggerDeferralState.ready_effects` then requires that chooser only when more than one effect is ready.

The key result is that ordering authority is branch-sensitive. If exactly one effect is ready, there is no alternative order to choose, so deterministic execution can continue even when selected rule sources would disagree about who controls a multi-effect choice.

The regression checks a Lost City/Reuniclus context. TPCi plus current Japan/Asia card-specific sources block a two-effect choice when current player and Knocked Out Pokémon owner are different players. The same claims resolve when both roles identify the same player. TPCi alone authorizes the current player, and missing context or an unauthorized submitter blocks the branch.

A second witness starts a sole Fainting Spell-like effect, records a Swelling Spite-like trigger while it is active, verifies that the new trigger is deferred, and starts it only after the active effect finishes. Both sole-effect starts need no ordering-authority decision.

Source authority and trigger deferral therefore constrain different boundaries: authority chooses among simultaneous ready alternatives, while deferral prevents interruption of the active effect.
