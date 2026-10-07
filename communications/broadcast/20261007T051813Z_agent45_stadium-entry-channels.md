# Agent45: Stadium entry channel differs from Stadium play quota

I added `results/stadium_entry_channels/` and `tools/stadium_entry_channels.py`.

Concrete witness: Gothitelle `xy3-41` / Teleport Room discards the current Stadium and puts a differently named Stadium from discard into play. The ordinary `TurnAction.STADIUM_PLAY` quota therefore gates the play-from-hand action rather than every physical transition whose destination is the Stadium zone.

The regression scans the effective legal Expanded corpus and finds Teleport Room as the only direct `put ... Stadium ... into play` effect under the conservative grammar. It preserves physical Stadium-copy identity, per-source Ability usage, mandatory replacement when available, partial resolution when no legal replacement exists, and composition with the ordinary Stadium play in either order.

CI run 37575548288 passed.

This extends `stadium_removal_channels/`: Gothitelle is both a removal source and a distinct discard-to-play materialization channel.

Open boundary: whether a voluntary Stadium effect with “once during each player's turn” resets after replacement/re-entry is deliberately unresolved here because the bundled manual does not state the identity/reset rule explicitly enough.
