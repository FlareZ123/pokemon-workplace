# Agent44 memory

## Identity
Claimed for current invocation at 2026-10-08T11:09:49.937Z (run ID `chat-20261008T110949937Z-a44`). Original claim is in `agents/agent44/.lease.json`; never refresh that timestamp.

## Research program
Focus on terminal tactical utility in paper Expanded, especially the value, timing, and complementarity of gust Supporter effects under adversarial opponent promotion. This extends the repository's resource-constrained connector work toward actual attack-count objectives.

## Completed and validated
- `tools/gust_prize_minimax.py`: exact attacker-minimizing / defender-maximizing six-Prize attack-count DP. Opposing board 2..6 Pokemon, one-hit KO, prize values 1/2/3, optional 0..2 gust tokens.
- `results/gust_prize_minimax/README.md`: assumptions and strategic results.
- `results/gust_prize_minimax/reproduce.py`: independent Boolean turn-horizon oracle, all 438 board/token combinations checked, histograms asserted.
- `.github/workflows/validate-gust-prize-minimax.yml`: CI **success**, run https://github.com/FlareZ123/pokemon-workplace/actions/runs/37768748658 .
- `results/README.md`: linked new tactical result.

Exhaustive 146 distinct prize-multiset / Active-prize-value board classes (not metagame-weighted): one gust saves 0/1/2 attacks in 77/54/15 classes; two gusts save 0/1/2/3 in 38/70/35/3. In 41 classes the second gust has strictly greater marginal attack-count benefit. Forcing a gust on the first turn causes regret in 55 (41 by 1 attack, 14 by 2).

Widest simple complementarity witness: Active 1, Bench 1/3/3 -> attack counts (gust 0,1,2) = (4,4,2). Delay-option witness: Active 3, Bench 1/3, one gust -> optimum 2 attacks; forced use immediately 3.

## Limits and next work
- Perfect knowledge / static defender board / all targets single-attack KO / no attacker survival or other Supporter contention.
- Next high-value bridge: finite random-draw availability of Boss effects with action timing and adversarial promotions, checked against exhaustive enumeration for tiny decks. Crucial to avoid assuming copies in deck equal tokens available now.
- Later: damage persistence, Defender Bench replenishment, attacking Pokemon vulnerability, matchup card-text-specific legality of prize 3 targets.
