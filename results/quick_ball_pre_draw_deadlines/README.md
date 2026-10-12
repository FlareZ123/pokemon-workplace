# Quick Ball opening access: separate pre-draw deadlines

## Research question

How much joint attacker-and-Gladion access is lost when one resource channel must be established **before** a scheduled natural draw?

The earlier [pre-draw option experiment](../quick_ball_pre_draw_option/) compared a player's choice to commit a payable Quick Ball early with waiting one draw. This extension imposes actual binary timing constraints on the same physical opening and Prize distribution. The computed difference includes cases where a future draw would have made a missing resource accessible too late to satisfy the earlier deadline.

The exact model is [tools/quick_ball_pre_draw_deadlines.py](../../tools/quick_ball_pre_draw_deadlines.py) and the independent [labeled-card reproducer](reproduce.py).

## Conditional 60-card environment

The deck contains one Tapu Lele-GX-like Basic, one required Basic attacker, ten other setup-eligible Basics, four critical non-starter singletons, two Gladion-like rescue Supporters, four Quick Ball, a specified number of dedicated disposable cards, and filler. Opening seven cards must include a setup-eligible Basic. Six Prize cards are then sampled without replacement. The outcome is conditioned on at least one modeled critical singleton being Prized. One later card is drawn naturally from the remaining deck.

Each Quick Ball searches exactly one available Basic after discarding one designated expendable card. Tapu Lele-GX supplies Gladion access only when hand-played onto the Bench and only if a Gladion remains searchable. A Tapu Lele-GX previously used as the setup Active Basic cannot simply retrigger its Wonder Tag. Searches account for all six hidden Prizes and remove physical targets from the deck before the natural draw.

The three conditions are:

1. **Both late:** attacker and Gladion objectives may be completed on either side of the natural draw, with the payoff measured immediately after it.
2. **Attacker early:** a held attacker or payable pre-draw Quick Ball search must establish the attacker before drawing; Gladion can be completed after the draw.
3. **Rescue early:** a held Gladion, a preserved hand-play Tapu Lele-GX with an available Gladion, or a payable pre-draw Quick Ball to Tapu Lele-GX plus Wonder Tag must establish Gladion access before drawing; the attacker may be completed after the draw.

The early-rescue route removes one Gladion from the deck before the draw. That detail matters for correct conditional draw probabilities.

## Exact result

| Dedicated disposable cards | Both after draw | Attacker before draw | Gladion before draw |
| ---: | ---: | ---: | ---: |
| 4 | 10.662593% | 9.225364% | 9.349409% |
| 8 | 14.762470% | 12.837763% | 13.061795% |
| 12 | **17.755369%** | **15.637331%** | **15.876092%** |
| 16 | 19.867280% | 17.728593% | 17.930759% |
| 20 | 21.294143% | 19.220246% | 19.362137% |
| 24 | 22.204606% | 20.222703% | 20.301070% |

The D12 deadline penalties are **2.118038 percentage points** for attacker-first and **1.879277 percentage points** for rescue-first. Both are larger than the **0.257277 pp** wait-versus-eager search-commitment difference in the companion result because the earlier deadline excludes states that can only be rescued by seeing a new card. These are different counterfactuals.

The model does not assume that a fixed target is available for Quick Ball search. A singleton attacker may already be among the six Prizes. Tapu Lele-GX or the last Gladion can be unavailable. Early success probabilities reflect those constraints.

## Verification

The implementation enumerates category allocations of the opening hand and Prize cards using exact multivariate combinatorial weights. For each eligible state, it conditions the permitted early action on real held Quick Ball copies and designated discardable cards, then exhaustively integrates the one-card natural draw.

An independent oracle labels every physical card, enumerates accepted opening hands and disjoint Prize configurations, and counts all physical draw outcomes. It checks all three conditions against the exact category calculation on two separate toy decks:

- 11 cards, four-card opening, two Prizes, one Gladion-like rescuer;
- 12 cards, four-card opening, two Prizes, two Gladion-like rescuers.

All three probabilities agree at absolute tolerance 1e-12. The complete 60-card baseline is cross-checked against the separately developed [pre-draw option model](../quick_ball_pre_draw_option/). The [focused CI workflow](../../.github/workflows/validate-quick-ball-pre-draw-deadlines.yml) passed at [run 38245697466](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38245697466).

## Scope and interpretation

This is a model of first-window access deadlines, with one natural draw provided externally. It does not measure actual attack legality, Energy attachments, evolution, turn-one Supporter restrictions, other search Items, Bench saturation, Item or Ability locks, real discard opportunity cost, ordinary Prize-taking, or opposing play. The modeled list intentionally differs from the tournament-derived decks in [competitive deck baselines](../competitive_deck_baselines/).

An attacker deadline can matter because the deck must establish a board or attack before the opponent develops a lock. Gladion's deadline depends on what becomes unavailable after a turn or which Prized resource must be recovered; the model assumes access matters immediately when the deadline is imposed, even though actually playing Gladion also consumes the Supporter turn.

The next research step is to use real deck-specific endpoints and time budgets: the card must be playable and the desired Prize recovery or attack must happen by its actual turn, under known opposing locks and available alternate actions. These numerical results are **conditional combinatorial findings**, not match win rates.
