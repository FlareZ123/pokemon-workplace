# Opposing Counter Catcher windows and Bench liabilities

## Question and bounded model

An extra Benched Pokemon may let an opponent use Boss's Orders for a decisive Prize-taking attack. Does the same liability exist for the more restricted Counter Catcher, and how large is the gap between conditional and unconditional opposing gust?

This study extends [reciprocal gust Bench liability](../mutual_gust_bench_liability/) with Counter Catcher on the **opponent's** side. Both players have fixed Prize-valued boards and limited, initially available gust resources. Boss has an unconditional target gust; Counter can gust while its player's remaining Prizes exceed the other player's. Opposing Counter eligibility is recalculated **after our Prize-taking attack**, before its reply. Both players choose their own new Active after a KO. The opponent may instead end the turn without attacking. Every attack is an immediate one-hit KO worth 1,2 or 3 Prizes. We start at six Prizes remaining with 2C/B+C/2B; the opponent starts at 2..6 Prizes and one of six resource inventories.

This is a public-state perfect-information game with no draw, evolution, HP, damage, Energy, Item lock, Supporter contention, or Bench development.

## Opponent-source Bench-addition census

Compare each original board with one additional Benched Pokemon worth 1/2/3 Prizes. Base states have our Active worth 1/2, eight own Bench configurations, six opposing gust inventories, 146 opposing Active/Bench classes, 2..6 opposing Prizes, and one of three own gust packages. There are **105,120** paired baseline/addition comparisons per opposing resource class.

| Opposing gusts held | Extra Bench turns win into loss | Extra Bench turns loss into win | Unchanged |
| --- | ---: | ---: | ---: |
| None | 0 | 15,467 | 89,653 |
| One Counter Catcher | 1,831 | 12,213 | 91,076 |
| One Boss's Orders | 4,914 | 10,378 | 89,828 |
| Boss + Counter | 6,151 | 7,852 | 91,117 |
| Two Counters | 2,552 | 10,102 | 92,466 |
| Two Bosses | 6,286 | 7,558 | 91,276 |

Even one opposing Counter can make adding a free Bench Pokemon harmful in this model. Across this enumeration, unconditional Boss poses a greater Bench exposure than one Counter. The source mix is stateful: Boss + Counter causes **6,151** harmful addition comparisons, more than either one-source inventory individually. The table describes structural comparisons with overlapping base states and no empirical metagame weights.

## A sharp conditional-versus-unconditional source gap

Our Active is worth one Prize, our Bench contains one- and three-Prize Pokemon, and the opponent has **three Prizes remaining**. We hold Boss + Counter. Across all 146 opposing board classes:

- Against one opponent Counter, we force a win in **96/146** classes.
- Against one opponent Boss, we force a win in **0/146** classes.

The reason is precise. Our first attack takes at most three Prizes, so our own remaining count falls from six to no fewer than three. With the opponent on three remaining, its Counter cannot be played on that first reply: their remaining Prizes do not exceed ours. An opposing Boss can immediately gust and KO our Benched three-Prizer for their last three Prizes. We cannot win on the first attack because no available opponent target is worth six Prizes. Hence the 0/146 unconditional Boss result is a consequence of these fixed initial conditions.

## Opposing Counter-specific exposed-Bench witness

We begin with six Prizes, Active worth one, Bench (1,1), holding Boss + Counter. The opponent has three Prizes remaining, Active two, Bench (2,2), holding one Counter. This initial state is a forced win. Add a three-Prize Pokemon to our Bench, and the opponent can force our loss. The opposing Counter is initially unavailable, then can become legal after we take Prizes. When its eligibility opens, the extra three-Prizer supplies a terminal target. Thus exposure can matter even if the opponent does not have immediate Boss access.

## Independent verification

The source is [tools/two_sided_bidirectional_gust.py](../../tools/two_sided_bidirectional_gust.py); the independent [deadline oracle](reproduce.py) checks **31,536** initial states. The model agrees with the prior reciprocal-Boss-only kernel on **15,768** further comparisons. It recomputes the full **630,720** Bench addition combinations and verifies that swapping an opponent Counter for unrestricted Boss cannot improve our forced-win result, the 96-versus-zero source gap, and the exposed-Bench witness.

Reproduction command: `python -m results.opposing_counter_bench_window.reproduce`.

## Limits

Actual Expanded play must include attack costs, HP, durability, Tools, Abilities, search/draw access to a gust, one-Supporter-per-turn contention, Item/Supporter locks, and cards in the Prize pile. A held-but-unplayable gust contributes no immediate target access. This result supplies a source-gate tactical regression for future stateful deck-optimization methods rather than claiming a tournament win rate.
