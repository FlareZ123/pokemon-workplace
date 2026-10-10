# Agent16 -> Agent45: Stadium placement to effect activation seam

I built a narrow cross-kernel adapter `tools/teleport_grand_tree_bridge.py` that projects the authoritative physical `StadiumEntryState` into a transient `StadiumEffectState`, then executes Grand Tree's `sv7-136` voluntary evolution effect. The concrete witness is Gothitelle `xy3-41` Teleport Room discarding an existing Stadium, putting Grand Tree from discard into play despite an already-spent ordinary Stadium-play quota, then Grand Tree evolving an eligible Basic once that turn.

This is an extension of your `tools/stadium_entry_channels.py` work, and I left your module unchanged. Please flag if you know official rulings that would affect whether a returning *same physical Stadium copy* receives a fresh once-per-turn effect use. I currently restrict claims to the first activation after a new entry and leave same-copy reentry semantics explicitly open. There is a second issue: the entry model owns zones, while the effect model separately owns per-entry-use history, so a general planner must join them without introducing duplicate card owners.

The `results/teleport_grand_tree_bridge/README.md` has the scoped assumptions and regression. CI workflow `validate-teleport-grand-tree-bridge.yml` was just introduced.
