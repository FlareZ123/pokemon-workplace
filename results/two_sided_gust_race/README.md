# Two-sided Prize race: optional Knock Outs and gust resource collapse

## Research question

The preceding [opponent Prize race](../opponent_prize_race_gust/) gives an exogenous scoring clock. Can the same Counter Catcher reopening be produced by Knock Outs on explicit opposing boards? Can an opponent's choice to skip an attack deny a gust-based forced win?

## Mechanically bounded two-sided model

Both players have fixed boards. A Pokemon is abstracted by the Prize value of knocking it out (1, 2 or 3). Attacks always knock out the chosen Active in one hit. We have zero or one targeted gust per attack and two total starting gusts: **2 Counter Catchers (2C)**, **1 Boss plus 1 Counter (B+C)**, or **2 Bosses (2B)**. The opponent has no gust, but selects its next Active after our Knock Outs. We select our own promotion after the opponent's Knock Outs. No new Pokemon enter play. We start at six Prizes remaining; the opponent starts with 3..6.

The opponent has two conditional policies: (a) KO our Active on every surviving reply, or (b) choose between that KO and ending the turn without attacking. The second option is permitted by the bundled Advanced Player's Rulebook A-01. The winner is whoever takes their last Prize or removes the other's final Pokemon. Current Counter Catcher eligibility is own remaining Prizes greater than opponent remaining Prizes. Other card search, damage thresholds, attack readiness, energy, Item locks and Supporter costs are omitted.

This is a mathematically exact perfect-information game under stipulations. It is **not** a measurement of match results or a general recommendation to delay attacks.

## Reproduced and novel structural counts

The study pairs **seven player boards** with all **146 opponent-board classes**, opponent remaining Prizes **3..6**, **three gust inventories**, and **two opponent attacking policies**, totaling **24,528 initial conditions**.

Counts below report opponent-board classes out of 146 where we can force a win. Each triple orders 2C / B+C / 2B.

| Our Active; Bench Prize values | Opponent Prizes | Opponent forced to KO | Opponent may pass | Newly denied by passing |
| --- | ---: | --- | --- | --- |
| 2; (2,2) | 4 | 75 / 75 / 75 | 51 / 75 / 75 | 24 / 0 / 0 |
| 2; (2,2) | 6 | 85 / 117 / 123 | 78 / 117 / 123 | 7 / 0 / 0 |
| 1; (1,2,2) | 6 | 141 / 141 / 141 | 141 / 141 / 141 | 0 / 0 / 0 |
| 1; (2,2) | 6 | 63 / 101 / 123 | 63 / 101 / 123 | 0 / 0 / 0 |
| 2; (1,3) | 6 | 117 / 123 / 123 | 117 / 123 / 123 | 0 / 0 / 0 |
| 1; (1,3) | 4 | 105 / 123 / 123 | 93 / 123 / 123 | 12 / 0 / 0 |
| 1; (1,3) | 6 | 75 / 111 / 123 | 72 / 107 / 123 | **3 / 4 / 0** |

The explicit player board of three two-Prize Pokemon, 2/(2,2), exactly reproduces the earlier exogenous fixed-two-Prize reply model: every surviving opponent KO removes one two-Prize target from our side. Allowing the opponent to pass corresponds to optional 0/2 Prize scoring. The independent comparison agrees for all 3,504 tested prior-model conditions.

## Mixed-inventory loss witness

Our side: Active worth 1 Prize, Bench worth (1,3). Opponent: **six Prizes remaining**, Active worth 1 Prize, Bench worth (1,1,2,3).

With one Boss and one Counter, we can force victory if the opponent must take the Active Knock Out each turn. When the opponent may legally pass, we **cannot** guarantee victory. Two Bosses remain a forced win under both response options; two Counters lose under both.

The full census shows **four** such mixed-resource state classes among 146 boards when our Active is one Prize and our Bench is (1,3), and the opponent has six Prizes. This distinguishes heterogeneous Prize-taking geometry from the all-two-Prize scenario, where an opponent's withheld KO only invalidated two-Catcher winning lines.

The tested assumptions are essential. An actual opponent may choose a non-KO attack, switch, heal, evolve, or progress its board. This abstract result shows the existence of state-dependent scoring deferral tactics, rather than confirming their strength in a particular real Expanded matchup.

## Independent validation

The main kernel is [tools/two_sided_gust_race.py](../../tools/two_sided_gust_race.py), using cached alternating minimax over our actions and promotions and the opponent's promotion and score/pass options. The [reproducer](reproduce.py) implements a separate finite-deadline Boolean feasibility oracle, which agrees on **24,528** state/policy conditions. It further makes **3,504** comparisons to the independently validated exogenous-score kernels, tests 2C <= B+C <= 2B and the exact mixed-inventory witness.

Execute from repository root: `python -m results.two_sided_gust_race.reproduce`.

## Next direction

Model actual attack costs, board survival and extra Bench development on both sides. Connect opponent's optional KO decision to the physical Prize reward of its targeted active and available alternative actions, then layer source-class Item/Supporter locks over the same two-sided transition model.
