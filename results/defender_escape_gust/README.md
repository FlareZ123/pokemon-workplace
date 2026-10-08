# Opponent escape resources reshape gust tactical value

## Question

The two-hit gust endgame model in `results/durable_gust_minimax/` assumes that a damaged opposing Active Pokemon stays Active until Knocked Out. What changes when the defending player can use a limited retreat-or-Switch-like effect on its own intervening turn?

## Model

`tools/defender_escape_gust.py` adds an integer `escapes` to the earlier minimax state. Every opposing Pokemon is `(Prize value, remaining hits)`, worth 1, 2, or 3 Prizes and requiring one or two attacks to KO. Damage persists across switches.

After a non-KO attack, the defender may leave the damaged Pokemon Active for free, or spend one escape token to switch it with a Benched Pokemon. The defender chooses the option giving the attacking player the highest eventual attack count. After an actual KO, the defender instead chooses a free replacement Active. An attacker may spend one gust token on an attack turn to bring a target from the Bench.

Victory occurs upon six Prizes taken or no opposing Pokemon in play. Neither player benches new Pokemon. The escape token is an abstract *already executable* switch/retreat action. Actual Energy payment, retreat locks, Supporter quotas, switching Items, opponent attacks, healing, and search access are outside the model. Hence the results condition on escape availability rather than infer it from a deck.

This is consistent with the advanced manual's normal once-per-turn Retreat (A-03), switching-by-effect distinction (C-03), and preservation of damage counters after moving a Pokemon to the Bench. The question of whether an escape is playable in a particular Expanded matchup is deliberately external.

## Complete finite-state census

Reuse all 390 board classes from `results/durable_gust_minimax/`: two to four opposing Pokemon from the six categories `Prize value 1/2/3` crossed with `one/two hits remaining`, requiring at least six total Prize rewards, and one selected starting Active class.

| Attacks saved by first gust | 0 defender escapes | 1 defender escape | 2 defender escapes |
| --- | ---: | ---: | ---: |
| 0 | 224 | 300 | 325 |
| 1 | 94 | 72 | 47 |
| 2 | 56 | 12 | 12 |
| 3 | 12 | 5 | 5 |
| 4 | 4 | 1 | 1 |

| Attacks saved by two gusts | 0 defender escapes | 1 defender escape | 2 defender escapes |
| --- | ---: | ---: | ---: |
| 0 | 122 | 151 | 168 |
| 1 | 105 | 127 | 136 |
| 2 | 126 | 78 | 58 |
| 3 | 30 | 29 | 24 |
| 4 | 7 | 5 | 4 |

A defender escape frequently devalues the earliest gust because the gusted two-hit target can be pulled away from the Active Spot before the finishing attack. In **79 of 390 classes**, permitting just one defender escape reduces the total attack turns saved by two available gusts.

There is also a more subtle reversal. The count of classes where the second gust has a strictly greater marginal attack-count benefit than the first is:

| Escape budget | Classes with increasing marginal gust value |
| ---: | ---: |
| 0 | 107 |
| 1 | 157 |
| 2 | 161 |

With one escape, **104 classes** newly acquire increasing second-gust marginal value that they did not have without escape. Thus a defensive switching capability can simultaneously reduce overall gust benefit and increase the degree of *complementarity* between gust copies. This is a structural property of the exact bounded state space and should not be interpreted as tournament frequency.

## A complete neutralization witness

Opponent Active `(1 Prize, 2 hits)`, Bench `(1 Prize, 2 hits)`, `(3 Prizes, 2 hits)`, `(3 Prizes, 2 hits)`.

| Defendant escape budget | 0 gusts | 1 gust | 2 gusts |
| ---: | ---: | ---: | ---: |
| 0 | 8 | 8 | 4 |
| 1 | 8 | 8 | 8 |
| 2 | 8 | 8 | 8 |

Without defender switching, two gusts can take two consecutive two-hit three-Prize knockouts in four attacks. With a single escape, after the first gust damages a three-Prize target, the defender can switch it back to the Bench before the second hit. That forces another targeting action and the two-gust four-attack win disappears against best defense.

The witness shows why static Prize rewards and gross gust copy counts are insufficient for a tactical model that omits what the opposing player does between hits.

## Validation

`results/defender_escape_gust/reproduce.py` independently determines win feasibility at each attack deadline, enumerating the attacker's target choice and defender promotion/escape responses. It checks every combination of the 390 boards, gust budgets zero through two, and defender escape budgets zero through two: **3,510 independent game-tree checks**. It additionally verifies all zero-escape results against the earlier durable minimax module (1,170 comparisons), invariants under increasing escape resources, both gain distributions, and the explicit witness.

Reproduce from the repository root:

`python results/defender_escape_gust/reproduce.py`

## Limits and next work

A real opponent must pay the retreat cost or possess an executable switching effect, may be locked, and might need its Active to attack. Our model gives an escape token unlimited target compatibility and no Energy or tactical cost. This is an adversarial escape-capacity upper bound.

The natural next step is to make escape reachability conditional on board Energy, retreat costs, switching cards, Item/Supporter lock, and whether leaving the damaged attacker Active preserves the opponent's own pressure. Reconnecting to stochastic gust access will reveal which counterplay windows actually matter at realistic hand and deck states.
