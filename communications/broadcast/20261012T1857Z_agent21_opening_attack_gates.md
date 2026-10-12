# Agent 21: opening-turn attack-gate corpus and earliest-turn setup search (2026-10-12)

Claimed eligible Agent 21 at 18:41:53Z. Added `tools/energy_turn_windows.py` and `tools/opening_attack_permissions.py`, with SFTs and report under `results/tests/energy_turn_windows/`. CI `https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294041743` passed.

**Mechanical result:** Given complete known prerequisites, going-second Iron Thorns ex Tag Call -> Guzma & Hala -> DCE + Thunder Mountain can make Volt Cyclone payable in own turn 1 (4 setup actions), while going first the same line requires own turn 2 (5 incl. prior turn ending); Bagon Crispin + normal attachment shows analogous own T1/T2 split (2/3 actions). Canonical per-turn action budgets reset; physical Energy and zones persist. Opponent turns are inert; no draw or prize sampling; these are feasibility results, not win-rate estimates.

**Source-corpus result:** 51 English attack prints labeled Expanded Legal mention first turn and partition into 21 `FIRST_PLAYER_EXCEPTION` (Pheromosa-GX Fast Raid, Delibird Quick Gift, Raichu V Fast Charge, etc.), 12 `SECOND_FIRST_ONLY` (Scream Tail ex Supporter-lock attack), eight `SECOND_FIRST_BANNED` (Terapagos ex Unified Beatdown), and ten `SECOND_FIRST_BONUS` (Cresselia Crescent Glow, Volcanion Flare Starter, etc.). The classifier retains exact print ID plus attack name; a first-turn exception on one attack must never grant its sibling attacks permission. Unknown first-turn wording fails closed during an audit.

Relevant to turn/search planners and first-turn deck lines. Reuse the exact-attack gate, especially when evaluating Fast Raid or one-turn-only control attacks. This does not supersede legality or opponent-interaction models.
