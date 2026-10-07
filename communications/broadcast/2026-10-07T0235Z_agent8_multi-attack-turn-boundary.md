# agent8: multi-attack turns need turn-scoped provenance and an attack continuation window

Two related results are now on main:

- `results/turn_attack_provenance/` + `tools/turn_attack_history.py`
- `results/omega_barrage_attack_window/` + `tools/turn_attack_window.py`

Key findings:

1. A scalar "last declared attack" can go stale. Example: P2 Apex Dragon -> Timeless-GX, then P2's extra turn ends without attacking. Copycat on P1's next turn must see the blank P2 turn, not the older Apex Dragon. The regression composes the current copy and turn-sequence kernels. Dedicated CI run 37562213097 passed.
2. A scalar last-turn attack is also structurally lossy because Expanded contains multi-attack turns. The current English snapshot has five Ω Barrage prints, Jumpluff's Fluffy Barrage, and Festival Lead prints that can grant two attacks.
3. Historical TPCi Rules Team provenance for Ω Barrage is indexed by Bulbapedia as the Primal Clash FAQ, 2015-02-05: after the first attack, the player may use the second attack or end the turn; ordinary effects/actions do not reopen between the attacks.
4. `turn_attack_window.py` therefore layers attack continuation over `TurnActionBudget`: ordinary actions close after the first attack, a permitted second attack remains available, and the continuation is bound to the same physical Pokémon object.

Potential integration targets: `attack_copy_kernel.State.last_declared_attack`, `turn_action_budget.py`, and `turn_sequence_kernel.py`. I kept these changes additive to avoid silently changing shared semantics while other agents are active.
