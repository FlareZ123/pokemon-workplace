# Energy movement conservation

This result treats an Energy move between two in-play Pokémon as a topology change of one existing physical card.

Implementation: `tools/energy_movement_conservation.py`  
Regression: `results/energy_movement_conservation/reproduce.py`

The test starts with one exchangeable Energy copy, materializes it as a physical instance, and attaches it to a source Pokémon.

A move changes the board holder from source to target and updates the identity ledger's `attached_to` relation to the same target. The same immutable Energy attachment object survives the transition and total card count stays one.

The card remains materialized because it never leaves board topology. This differs from retreat discard or board removal, where an attachment returns to an ordinary zone and can become exchangeable again.

The helper assumes an upstream card effect has already established that the move is legal for the destination Pokémon. Card-specific attachment restrictions are outside this bridge.
