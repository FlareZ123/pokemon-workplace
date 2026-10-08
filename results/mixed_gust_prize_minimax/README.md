# Mixed Boss + Counter Catcher: an expiring-gust scheduling result

## Question

How much value is recovered by replacing one of two Counter Catchers with one
unconditional Boss's Orders, and which gust should be spent first when both are
available?

This extends [Counter Catcher Prize timing](../counter_catcher_prize_timing/)
and the [bounded gust minimax](../gust_prize_minimax/). It tests a resource
allocation issue behind associativity-based deck evaluation: two cards with
identical targets may still have different continuation value because their
permission windows have different deadlines.

## Card rules and bounded model

Counter Catcher is an Item that can gust an opposing Benched Pokemon only
while the acting player has **more Prize cards remaining than the opponent**.
Boss's Orders is a Supporter that can gust an opposing Benched Pokemon without
this Prize threshold. Their different Item/Supporter action classes matter in
real play, but both are presumed executable when their modeled conditions hold.

The player begins at six remaining Prizes. The opponent's remaining Prize
count is held fixed at one of 1, 2, 3, 4 or 5. There are two already available
gust cards in one of three inventories: **two Catchers**, **one Catcher plus
one Boss**, or **two Bosses**. Each gust chooses any opposing Benched Pokemon
and is consumed. The player may use at most one strategically meaningful gust
before each attack; a no-gust attack is always allowed.

The opponent begins with 2..6 Pokemon, each worth 1, 2, or 3 Prize cards and
Knocked Out by a single attack. Each KO reduces the player's remaining Prize
count before another turn can use Counter Catcher. Following each KO, the
defender adversarially chooses the next Active Pokemon. Taking six Prizes or
Knocking Out the final opposing Pokemon wins. No new Pokemon, draw, healing,
Item lock, opponent attacks, or support actions are modeled.

This is **146 distinct board classes**, not a weighted competitive metagame.

## Exhaustive mixed-inventory census

Exact minimax number of attacks, summed across the 146 board classes:

| Opponent Prizes | 2 Catchers | 1 Catcher + 1 Boss | 2 Bosses |
| ---: | ---: | ---: | ---: |
| 1 | 392 | 392 | 392 |
| 2 | 398 | 392 | 392 |
| 3 | 480 | 392 | 392 |
| 4 | 516 | 398 | 392 |
| 5 | 516 | 398 | 392 |

Counts of board classes where the mixed inventory improves on two Catchers or
loses to two Bosses:

| Opponent Prizes | Mixed strictly better than 2 Catchers | Mixed strictly worse than 2 Bosses |
| ---: | ---: | ---: |
| 1 | 0 | 0 |
| 2 | 6 | 0 |
| 3 | 76 | 0 |
| 4 | 94 | 6 |
| 5 | 94 | 6 |

For opponent Prizes **1..3**, one Boss plus one Catcher matches two Bosses on
**every** tested board class. At 4..5, six boards require two unconditional
gust opportunities after an otherwise useful natural attack, so the mixed
inventory loses one attack in those classes. These are board-structural results
under the stated fixed-opponent-Prize assumption.

## Two complementary tactical witnesses

### Case A: mixed inventory restores the two-attack win

Opponent has **3 Prizes remaining**; its Active Pokemon is worth **3 Prizes**
and Bench contains a **1-Prize** and **3-Prize** Pokemon.

| Gust inventory | Minimax attacks |
| --- | ---: |
| Two Counter Catchers | 3 |
| One Counter Catcher + one Boss | **2** |
| Two Boss's Orders | **2** |

A three-Prize KO decreases our remaining Prizes to three, disabling further
Counter Catcher use. With the mixed inventory, use **Counter Catcher first**
to KO the Benched three-Prize Pokemon, then use the retained Boss to gust and
KO the other three-Prize Pokemon. The two-Catcher inventory cannot perform the
second gust through the tie.

### Case B: unconditional supply still matters

Opponent has **4 Prizes remaining**; its Active Pokemon is worth **2 Prizes**
and the Bench contains **1, 2, 2 Prizes**.

| Gust inventory | Minimax attacks |
| --- | ---: |
| Two Counter Catchers | 4 |
| One Counter Catcher + one Boss | 4 |
| Two Boss's Orders | **3** |

Two Bosses allow the natural two-Prize Active KO first and targeted KOs on
the other two two-Prize Pokemon next. But taking the natural first KO reduces
our remaining Prizes from six to four, making Counter Catcher unusable. Spending
Catcher before this threshold closes leaves insufficient future gust capacity
against adversarial promotion. This is a precise case where a mixed package
cannot replace two always-available gusts.

## Exchange argument: use an expiring gust before its unrestricted substitute

Under the assumptions above, own remaining Prizes decrease monotonically and
the opponent's count stays fixed. Counter Catcher's permission
`own_prizes > opponent_prizes` therefore only becomes *harder* to satisfy.

**Conditional source-priority theorem:** when a targeted gust is already
chosen for the current turn, both Boss and Catcher are available, and Catcher
is currently legal, spending Catcher instead of Boss cannot worsen the
optimal future attack count. To prove this, copy the Boss-first target
choice and swap the source labels: use Catcher now and save Boss for any
later gust opportunity. Boss can replicate the unrestricted target of the
original later Catcher, whether the threshold remains open or closes.
If the original plan never uses the Catcher, retaining Boss is at least
as useful as retaining the expiring Catcher.

The exhaustive census confirms this priority on all **730 initial board /
opponent-Prize scenarios** with one of each gust. Strict improvement in
minimum attack count from forcing Catcher first rather than Boss first occurs
in **0, 0, 73, 94, 100** of the 146 classes at opponent Prize counts
1, 2, 3, 4, 5 respectively.

**Important:** the theorem assumes that a gust is being used now. It does
not say that a gust should be used eagerly. With Active 2 and Bench 1/2/2,
opponent at three Prizes, the mixed inventory wins in three attacks by
taking the natural Active KO and saving both gusts. Forcing Counter Catcher
on the first turn requires four attacks.

The exchange argument can fail once Item lock, Supporter competition, card
access, on-play side effects, heterogeneous targets, or opponent Prize
changes are modeled. The result is a deliberately narrow benchmark for
future richer policies.

## Validation and reproducibility

- Model: `tools/mixed_gust_prize_minimax.py`
- Independent regression: `results/mixed_gust_prize_minimax/reproduce.py`
- The independent solver asks whether victory is possible by a given fixed
  attack deadline, using existential attacker actions and universal defender
  promotion, rather than minimizing attack counts directly.
- It verifies **2,190 distinct initial board/inventory/Prize scenarios**,
  plus exact agreement with the previous two-Catcher and two-Boss engines.
- It checks all table sums, 730 source-priority comparisons, and the three
  tactical witnesses above.

## Further research

Add a typed action budget and board-state gate. Boss consumes a Supporter
action, while Counter Catcher is blocked by Item lock. Recompute source-priority
when another Supporter must be played on the same turn or when Item lock is
expected to become active. Also distinguish opponent Prize paths that reopen
the Counter Catcher window, without granting free opponent Prize-taking that
would unrealistically help the player.
