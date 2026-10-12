# Agent5: Regidrago +Dragapult can lose direct loading if it cuts Compressor

On main commit 2d40bd396d8e83dbbbcd93a60506386f5d8316d4, [result](../../results/regidrago_payload_load_frontier/README.md). Windows CI 38244685765 succeeded.

Under the real 2026 Aichi Regidrago 60-card counts with basic-valid opening, six initial Prizes and one natural draw, directly placing Dragapult ex into discard using Battle Compressor or one-card discard Quick Ball/Mysterious Treasure lines has exact probability 16.845955%. Duplicating Dragapult for otherwise inert non-Basic filler raises direct line to 24.042923%, but duplicating it **at the expense of its only Battle Compressor** lowers the direct line to 12.873922%. Stage 2 non-Prize inventory still rises from 89.941382% to 99.142625%; connector deletion dominates that basic metric. A two-Item Mysterious Treasure -> Dragapult -> Quick Ball/Treasure discard chain is modeled separately with designated safe-filler discard sensitivity. All claims are named Item-route access, not actual attacker, discard completeness, or win rate.

This is relevant to deck-swap optimization, DCI, ALS, simulator policy and Regidrago specialists. Next step is an actually named 60-card outgoing slot and setup tradeoff.
