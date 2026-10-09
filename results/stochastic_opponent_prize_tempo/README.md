# Counter Catcher creates a non-monotone opponent-scoring incentive

## Question and model

Can the opponent becoming more likely to take Prize cards sometimes **increase** our winning chances? It speeds up their race, but may reactivate Counter Catcher after we take Prizes. This extends the [deterministic Prize race](../opponent_prize_race_gust/) benchmark.

The attacker starts with six Prizes and fully available 2 Counter Catchers (2C), 1 Boss + 1 Counter (mixed), or 2 Bosses. The defender has 1..6 Prizes and a 2..6-Pokemon board with 146 Active/multiset classes. Each target is a one-attack KO worth 1, 2 or 3 Prizes; the defender chooses each new Active adversarially. After each nonwinning attack, the opponent independently takes two Prizes with probability p and none with probability 1-p. The attacker observes this outcome before its next action; reaching zero opposing Prizes means an immediate loss.

The model uses exact rational extensive-form minimax. The opponent's scoring options are **hypothetical external assumptions** rather than validated attack-ready board actions or empirical probabilities.

## A counterintuitive exact witness

Opponent has four Prizes remaining; its Active is worth three and Bench is worth (1,1,3). We hold two Counter Catchers. The optimal win probability at the tested rational p values follows:

**P(win) = 1 - (1-p)p².**

| Opponent two-Prize-scoring probability | Optimal win probability |
| ---: | ---: |
| 0 | 1 |
| 1/4 | 61/64 |
| 1/2 | 7/8 |
| 3/4 | 55/64 |
| 1 | 1 |

At p = 2/3 the displayed polynomial reaches its minimum, **23/27**. The effect is nonmonotone: raising the opposing scoring probability from 3/4 to 1 actually improves our chance in this controlled game.

One optimal line takes the natural three-Prize Active KO first. If the opponent then takes two Prizes, their count drops from four to two while ours is three; Counter Catcher reopens, allowing us to gust the Benched three-Prizer and win with the second attack.

If the opponent initially takes none, the defender can promote a one-Prizer. After our next one-Prize KO, an opponent two-Prize score creates a tie at two Prizes each, still blocking Counter. Another two-Prize score before the fourth attack ends the game. The losing reply sequence is zero, then two, then two, probability **(1-p)p²**. At p=0 there is unlimited time to clear the board. At p=1 the first opposing score makes the winning Counter line available immediately. One Boss plus one Counter or two Bosses win this witness with certainty for all tested p.

## Exhaustive exact results

Five rational values p=0,1/4,1/2,3/4,1 across six opponent-Prize counts, three inventories and 146 classes give **13,140** exact outcomes. Counts of board classes whose optimal win probability increases between at least one adjacent pair of tested p values:

| Opponent Prizes | Two Catchers | Mixed | Two Bosses |
| ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 |
| 4 | **24** | 0 | 0 |
| 5 | 0 | 0 | 0 |
| 6 | **7** | 0 | 0 |

We also analyzed an opponent who can **choose** whether to take zero or two Prizes each surviving turn. Among **2,628** initial board/inventory/score states, exactly the same 24 and 7 two-Catcher boards change from forced wins under constant two-Prize opposing progress into potential losses when the opponent can strategically withhold a KO. The mixed and two-Boss packages have no such withheld-scoring reversal in this dataset.

The source nesting remains valid throughout: 2C optimal win probability <= mixed <= 2B. The fact that more opponent scoring can help a Counter deck is a structural interaction between Prize gates and time-to-victory, not an unconditional recommendation for the opponent to avoid taking Prizes.

## Reproduction and limitations

- [Exact rational kernel](../../tools/stochastic_opponent_prize_gust.py)
- [Reproducer](../opponent_prize_race_gust/stochastic_reproduce.py)
- [Deterministic clock oracle](../opponent_prize_race_gust/)

The stochastic solver matches the independent deterministic model at p=0 and p=1. The witness polynomial is checked at 21 rational points and was also checked on a denser 101-point local grid. Every selected interval comparison is evaluated exactly. The opponent's adaptive choice of zero or two scoring Prizes is tested through a separate Boolean game.

Run from repository root: python -m results.opponent_prize_race_gust.stochastic_reproduce.

The score process is external. It does not prove that the opponent has access to a two-Prize KO, that refusing to attack is better in a particular real match, or that these 146 abstract board classes have uniform competitive frequency. An important next step is to tie opponent scoring to actual attacker Energy, damage, the other player's vulnerable Pokemon, and legal turn actions.
