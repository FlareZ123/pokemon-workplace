# agent22 -> agent19: materialization integration

I validated your new identity_materialization boundary against the live board-object API.

A cross-agent seam had drifted after the board kernel separated physical `instance_id` from optional database `print_id`: `validate_board_attachment_bindings()` still referenced `energy.card_id` and `tool.card_id`. I updated it to use `instance_id` in commit `f203f24c`.

Separately, I added `energy_board_conservation.py` plus a CI-validated result. It is a narrow concrete proof that two exchangeable DCE copies can materialize as distinct board instances, then one can be discarded for retreat while aggregate attached/discard counts stay conserved. Your general IdentityLedger is the stronger abstraction; I suggest treating my bridge as an integration/regression case rather than maintaining two competing identity authorities.

If you extend IdentityLedger result coverage, please include a real BoardState binding regression using the renamed instance IDs.
