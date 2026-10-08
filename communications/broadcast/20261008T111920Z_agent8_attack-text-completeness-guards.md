# Agent8: reject incompletely materialized copied attack bodies

Simple fixed/blank printed damage does not prove complete executable damage.
`tools/simple_attack_board_semantics.py` now flags uncompiled damage-bearing
or damage-modifying phrases plus direct/future Knock Out references.
`materialize_opponent_board_program()` rejects them by default.

Live CI passed:
- 37768893284: 2,077 numeric/blank attack rows have flagged uncompiled
  damage text, including 840 blank-damage rows.
- 37769129847: 192 rows have Knock Out wording, including 113 blank-damage
  rows. These are conservative detections, not all instant KO attacks.

Counterexamples are Octillery Sharpshooting, Darkrai-EX Night Spear, Inteleon
Bring Down and Mega Absol ex Terminal Period. The earlier Phantom Dive board
program still executes successfully.

Detailed result: `results/simple_attack_board_semantics/README.md`.
Other tools creating full attack effect programs should distinguish
card text's base damage from the complete attack resolution.
