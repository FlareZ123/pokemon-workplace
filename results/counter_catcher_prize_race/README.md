# Counter Catcher timing reverses when the opponent also takes Prizes

## Question

The earlier `counter_catcher_prize_timing` result showed that taking high-value opposing Knock Outs can make Counter Catcher ineligible for the next turn. That study held the opponent's remaining Prize cards constant. Since a real opponent may take Prizes during intervening turns, can opponent progress *reopen* the item-gust window, and does that improve the attacker enough to survive?

## Controlled clock model

`tools/counter_catcher_prize_race.py` tracks both players' remaining Prize counts.

On each attacker's turn the attacker can KO the current Active or, if permitted, consume one Boss's Orders-like gust or Counter Catcher-like targeted gust to KO a Benched Pokemon. Each opposing target needs one attack and gives 1, 2 or 3 Prizes. The defender chooses the next Active adversarially after KO.

If the attacker's action does not win immediately, the model assumes that during the opponent's ensuing turn the opponent takes **exactly 0, 1, or 2 Prize cards**, whichever fixed `opponent_pace` is selected for that scenario. If the opponent takes their last Prize first, the attacker loses: no further attacker turn occurs. This is an *exogenous opponent progress clock*, not a claim that the opposing board can always attack or secure such a KO. There are no effects of opponent attacks on our Bench, no new opposing Pokemon, no extra Prize taking outside the fixed clock, and no draw or Supporter access probabilities.

Counter Catcher is playable at the moment of each targeted gust only when **our Prizes remaining exceed our opponent's**. A Boss-style gust has no such gate. Both are assumed to be available and to cost one distinct attack-turn targeting opportunity.

The bundled Counter Catcher `sv4-160` text grounds the condition. Advanced rulebook B-01/ B-03, D and E specify the Item/Supporter windows, KO/Prize sequence and win conditions.

## Exact census

All **146** source boards from the one-hit gust minimax are tested against fixed opposing Prize counts and opponent progress rates 0, 1, or 2 per opponent turn.

The following table compares two initially available Counter Catchers against two unconditional Boss-style gusts:

| Opponent Prize clock | Opponent starts with | Both can force win | Neither can force win | Only Boss can force win |
| ---: | ---: | ---: | ---: | ---: |
| 0 Prizes per turn | 3 | 146 | 0 | 0 |
| 1 Prize per turn | 3 | 123 | 23 | 0 |
| 1 Prize per turn | 4 | 141 | 5 | 0 |
| 2 Prizes per turn | 6 | 85 | 23 | 38 |

Among boards where both can win, extra attacker turns required by two Catchers relative to two Boss effects are:

| Opponent clock / initial Prizes | Equal attack count | Catcher needs +1 | Catcher needs +2 |
| --- | ---: | ---: | ---: |
| 0 / 3 | 70 | 64 | 12 |
| 1 / 3 | 123 | 0 | 0 |
| 1 / 4 | 65 | 64 | 12 |
| 2 / 6 | 35 | 50 | 0 |

These are **uniform structural counts** of an artificial game state space. They should not be interpreted as prevalence estimates of competitive matchups.

## Witness A: the opposing Prize gain restores the saved Catcher

Start: opponent Active is worth **3 Prizes**, Bench **1 and 3 Prizes**. Attacker has six Prizes remaining and defender three. The attacker possesses two otherwise executable Counter Catchers.

If the opponent takes **zero Prizes** between our turns, KOing the initial Active for three Prizes leaves each player with three. Our saved Counter Catcher becomes unplayable, and the defender can force a **three-attack** finish.

If the opponent takes **one Prize** between our turns, after the same initial KO we have three remaining and the opponent now has two. Counter Catcher becomes playable again on our next turn, targeting the three-Prize Bench Pokemon. We win in **two attacks**, matching an unconditional Boss gust.

The opponent's offensive progress restores Item usability, even while also reducing our time to win.

## Witness B: late Catcher eligibility can miss the race deadline

Start with **six Prizes remaining each**. Opponent Active is worth **1 Prize**, Bench **1, 3 and 3 Prizes**. Opponent's assumed pace is **two Prizes per turn**.

Two unconditional Boss gusts can target both three-Prize targets immediately and win in **two attacks**.

Counter Catcher is initially unavailable while the Prize counts are tied. The attacker must first KO the one-Prize Active. After the opponent takes two Prizes, a Catcher becomes available, but the attacker cannot force the six-Prize victory before the opponent's subsequent Prize clock expires. The model marks this route as a **loss**.

The Catcher becomes usable, yet its timing is insufficient to satisfy the required deadline.

## Verification

`results/counter_catcher_prize_race/reproduce.py` independently checks whether each state has a guaranteed win within a bounded number of attacker turns. The exhaustive comparison covers **15,768** board / source / gust-budget / opposing Prize-count / opponent-pace combinations: 146 boards × 2 sources × 3 gust counts × 6 opposing Prize counts × 3 pace values. With zero opponent progress, all Counter Catcher results reduce exactly to the earlier `counter_catcher_prize_timing` solver, and all unrestricted results reduce to `gust_prize_minimax`.

Run: `python results/counter_catcher_prize_race/reproduce.py`.

## Interpretation

Counter Catcher's tactical value depends on the joint sequence of Prize cards taken by **both** players. Its condition can close after a successful high-Prize KO and reopen after an opposing KO. But a fast opponent may also end the match before a reopened opportunity can be executed.

A realistic match model requires conditional probabilities of opponent KO targets, survival of the attacker's board, game-state-dependent retreat/disruption, and search access. This clock model provides a verified intermediate representation and exposes why static Prize-count arguments should remain conditional.
