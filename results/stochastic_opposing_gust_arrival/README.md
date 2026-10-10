# One hidden opposing gust: draw timing and Bench liability

## Question and model

Earlier [opposing Counter Bench window](../opposing_counter_bench_window/) and [bidirectional gust](../../tools/two_sided_bidirectional_gust.py) results assume the opponent already holds its Boss's Orders or Counter Catcher. This experiment places **one** opposing gust source uniformly among `N` unseen cards instead. On every opposing reply, the opponent draws one card and, if the hidden source appears, may use it that turn. The drawn source and its arrival are **publicly revealed** in this controlled information model. A source that has been played is spent.

The remaining game is the same deliberately abstract two-sided Prize race: each player has a fixed board of 1-, 2-, and 3-Prize Pokémon; attacks always knock out the selected Active Pokémon; one side can expend up to two initially held Boss / Counter gusts; the opposing side has the single hidden source. The opponent chooses which of its survivors to promote after our KO, and we choose ours after its KO. The opponent may end a turn without attacking. Both sides act optimally to maximize or minimize our exact eventual win probability. The player always attacks on their turn.

The opposing hidden source is either unconditional **Boss** or prize-gated **Counter Catcher**. The source is an abstract already-usable card when drawn; source-class action permissions, Trainer locks, and Supporter contention are outside this version.

## Exact chance node

With `n` unseen slots containing exactly one source, the next opposing draw reveals it with probability `1/n`. If missed, `n-1` unseen slots still contain that source; subsequent draws continue this without replacement. Once held, it remains available until used, and cannot be drawn again. The minimax engine calculates rational `Fraction` probabilities, retaining the opponent's optional choice to pass so Counter's eligibility can change after our future KOs.

This explicit arrival-state distinction matters: a Counter may be drawn while unusable, held through an intentional pass, and used after our next knockout moves the Prize differential.

## Two exact witnesses

**First-reply Boss exposure.** Our Active is worth one Prize, Bench has one one-Prizer, and we hold two Counter Catchers. Opponent has two Prizes remaining and Active/Bench (3,3). Adding a two-Prize Pokémon to our Bench converts certain victory into a conditional loss if the opponent draws its hidden Boss **on its first reply**. The exact post-addition win probability is `(N-1)/N`; baseline remains 1. The same hidden Counter fails to generate a loss here, even if drawn, because its Prize gate stays closed.

**Two-reply Counter exposure.** Our Active is worth one Prize, Bench is (1,1), and our gust resources are Boss + Counter. Opponent has three Prizes remaining and Active/Bench (2,2,2). Adding a three-Prize Benched Pokémon creates a terminal target. For either opposing hidden Boss or Counter, our win probability after addition is `max(0,(N-2)/N)`, while the smaller starting Bench gives 1. Counter can be held while initially illegal: the opponent **passes** after our first two-Prize KO, then our second two-Prize KO opens its Counter gate. A draw on either of the first two opposing replies suffices for the opponent's winning gust. This is a conditional demonstration of Prize-withholding interacting with actual card access.

| Unseen card slots `N` | First-reply Boss witness | Two-reply Boss / Counter witness |
| ---: | ---: | ---: |
| 1 | 0 | 0 |
| 2 | 1/2 | 0 |
| 4 | 3/4 | 1/2 |
| 8 | 7/8 | 3/4 |
| 16 | 15/16 | 7/8 |

Values in the table are **our** modeled win probabilities after adding the vulnerable Bench Pokémon. No value is a tournament win rate.

## Fixed-support 39-board comparison

To compare source types on identical opponent structures, enumerate all 39 classes of 2 to 4 opposing Pokémon whose total available Prizes are at least six, with opponent Prizes remaining 2 or 3. For each class, our starting board is Active 1, Bench (1,1), and our inventory is Boss + Counter. Compare this with adding one three-Prize Benched Pokémon. There are 78 comparisons per opposing source and unseen-pile size.

| Opposing hidden source | `N` | Bench addition lowers our win probability | Raises it | Same |
| --- | ---: | ---: | ---: | ---: |
| Boss | 1, 2, 4, 8 | 52 / 78 | 0 | 26 / 78 |
| Counter | 1, 2, 4, 8 | 9 / 78 | 0 | 69 / 78 |

For Boss at `N=1,2,4,8`, strictly partial probabilities occur in 0,36,52,52 of its 52 harmful cases. For Counter the corresponding counts are 0,0,9,9. Delay changes how severe the cases are even when the set of harmed structural states stays constant. This is a deliberately restricted, unweighted census and should not be extrapolated to the Expanded metagame.

## Verification and reproducibility

Run `python -m results.stochastic_opposing_gust_arrival.reproduce` from the repository root. It verifies:

- **5,616** exact all-source, all-in-hand equivalences against the prior deterministic solver at `N=1`;
- closed-form probabilities on both witnesses for each `N=1..16`;
- **624** fixed-support stochastic Bench comparisons reproducing the table;
- source containment: a hidden unrestricted Boss never improves our optimal win probability over an identically timed hidden Counter in the tested structural states.

Source: [tools/stochastic_opponent_gust_arrival.py](../../tools/stochastic_opponent_gust_arrival.py). The probability calculations are exact under the model, with no Monte Carlo sampling.

## Limitations and next research

Public revelation is an **information upper bound for our policy** compared with normal hidden opponent hand contents. Actual play would include a seven-card starting hand, six Prize cards, changing deck size, opponent search or draw engines, attacker HP, Energy readiness, KO damage, both players' Bench development, locks, alternative Supporter uses, and opponent selection of draw/disruption actions. The experiment conditions on the opponent having exactly one source in the unseen draw population, and does not model how often that condition occurs.

One fruitful next step is a belief-state model where the opponent knows whether its card was drawn while we observe only revealed play. Another is coupling physically executable gust actions and opponent attack readiness to the same finite draw process.