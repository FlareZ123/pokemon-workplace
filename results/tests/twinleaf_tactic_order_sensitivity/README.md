# Native Twinleaf versus attack-before-retreat: controlled policy sensitivity

## Hypothesis

The pinned Twinleaf `SimpleTacticsAi` executes `RetreatTactic` before `AttackTactic` (after its other setup actions). That ordering, plus scalar state scoring, may determine whether a developed attacker is used or retreated. A small research-owned intervention swaps only those two upstream tactic constructors. The actual card implementations, attack and retreat rules, complete decklists, and game random source remain unchanged.

[`simulation/twinleaf/tactic-order-policy.cjs`](../../../simulation/twinleaf/tactic-order-policy.cjs) implements two explicit orders: `native` and `attack_before_retreat`. It asserts the pinned native order has not changed and never mutates the upstream array. Its [standalone regression](../../../simulation/twinleaf/test-tactic-order-policy.cjs) checks identity, idempotence and invalid pinned assumptions. Manual [workflow](../../../.github/workflows/twinleaf-manual-matchup.yml) selects both decks, 1–3 paired seeds, and the tactic order.

## Matched input conditions

- Tournament-derived, exact mapped and card-text checked paper Expanded [Shadow Rider Calyrex](../../decks/shadow-rider-calyrex/) and [Regidrago VSTAR](../../decks/regidrago-vstar/), physical printed 60-card lists unchanged between conditions.
- Twinleaf pin `3348ebdc898f175a2ed8f999133cd13d1afd01f5`; Fisher–Yates shuffle research hook, isolated live-game and hypothetical-policy random streams, 350 actions and 25 seconds max per game.
- Two seed pairs `20261012` and `20261013`, each with two seat orientations. The identical seed numbers are a starting-state control, although action-path differences can change the subsequent random draw count and card-order trajectories.
- Native runs [38293750862](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293750862) and [38293905086](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293905086); alternative run [38294612961](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294612961). All relevant steps passed.

| Seed | Seat 1 | Seat 2 | Native winner | Attack-first winner |
| --- | --- | --- | --- | --- |
| 20261012 | Shadow Rider | Regidrago | Shadow Rider | Shadow Rider |
| 20261012 | Regidrago | Shadow Rider | Shadow Rider | Regidrago |
| 20261013 | Shadow Rider | Regidrago | Shadow Rider | Regidrago |
| 20261013 | Regidrago | Shadow Rider | Shadow Rider | Shadow Rider |

**Observed sensitivity:** native bot configuration finished 4–0 Shadow Rider; attack-first finished 2–2. Every game reached the native engine's terminal state with no error or censor. Two of the same-seed, same-seated comparisons changed which deck won after a single tactic-priority intervention. This demonstrates sensitivity of *this headless evaluation*, not superiority of the alternative policy or a true match win rate.

## What the actual action traces show

In the alternative seed-20261012 game with Regidrago seat 1, it used `Celestial Roar` three times followed by `Dragon Laser` six times, took all six Prize cards, and won on turn 18. In the native version of the same orientation, Regidrago used `Celestial Roar` once and `Apex Dragon` once, passed sixteen turns, took no Prize cards and lost on turn 37. The behavior change materially altered attacker use and game length.

The other Regidrago win, alternative seed-20261013 with Regidrago in seat 2, illustrates a separate failure mode: Regidrago **never attacked** and neither player took a single Prize. Shadow Rider's bot repeatedly used `Filch` (eleven times) and `Copycat` (eleven times), and decked out on turn 46. [The repeat with terminal-state logs (run 38294908202)](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294908202) recorded the Shadow Rider deck at zero cards, the Regidrago deck at 17 cards, and explicit `LOG_PLAYER_NO_CARDS_IN_DECK` for Shadow Rider followed by `LOG_GAME_FINISHED_WINNER` for Regidrago. Both decks still had six Prizes. Calling this a Regidrago attack-plan victory would be incorrect.

The policy mechanism is a real executable effect: pinned `simple-tactics-ai.ts` selects the first valid tactic in the declared list, and the upstream `AttackTactic` and `RetreatTactic` each simulate hypothetical outcomes with coarse state scores. The research-side order exchange changes what action is tried first. It does not validate human game tactics or copy-attack target choice.

## Strategic implications and limits

An apparently decisive model score can reverse with a small decision-rule change. **No ranking between the source tournament decks is justified by these games.** Further work requires strategic policy design for `Apex Dragon`, Dragon discard setup and copying, Prized payload management, gust, Item lock, and early Bench construction, followed by attacks/effects tests and broader opponent sampling. A genuine match-strength study must report the policy and its demonstrated proficiency per archetype as prominently as the headline win counts.

Evidence: pinned source-level implementation, independent standalone policy SFT, real 60-card headless games with exact seat and seed tags, and reproducible terminal logs. The policy is a counterfactual research tool, not an optimized competitor.
