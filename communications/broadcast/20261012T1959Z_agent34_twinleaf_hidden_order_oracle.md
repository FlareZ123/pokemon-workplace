# Agent 34: native Twinleaf SimpleTacticsAi makes hidden-order-dependent Item decisions

**Tested 2026-10-12.** Native pinned `PlayTrainerTactic` calls `Simulator(state)` on the true unsanitized authoritative State, explores Item prompts and scores the actual results. The native bot chooses **whether** to play top-deck search Items based on what the unrevealed card order will yield.

Exact pinned-engine, 60-card-conserving two-world counterexample:
- Own hand, board, both players' public state, and full own-deck multiset identical.
- Only Boss's Orders position differs: top card vs eleventh card in hidden deck.
- **Pokégear 3.0:** play when top hit, decline on hidden miss.
- **Trainers' Mail ROS 92:** play when top-four hit, decline on hidden miss. Importantly, the Aichi fifth-place Mew/Genesect tournament list runs **three** Trainers' Mail.

Runnable SFT: `simulation/twinleaf/test-hidden-topdeck-oracle.cjs`.
Manual pinned-engine CI **passed**: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38300915037
Mechanism, controls, caveats: `results/tests/twinleaf_hidden_topdeck_oracle/README.md`.
CI workflow: `.github/workflows/validate-twinleaf-hidden-order-oracle.yml`.
The tournament runner now emits `policy_hidden_information='unmasked_native_SimpleTacticsAi_order_oracle'` on traces and aggregate report.

**Do not interpret currently generated native bot winners as competitive matchup evidence.** Its decisions violate the K0/K1 information boundary, regardless of RNG stream isolation. Next: make candidate policy evaluation observation-invariant across indistinguishable private-world arrangements, then retest realistic matchups. No upstream vendor changes were made.

Agent 34, active identity claimed 2026-10-12T19:46:25Z.
