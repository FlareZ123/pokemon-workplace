# Target multiplicity and the Crobat/Dedenne draw frontier

## Question

The [single-target sequencing study](../bench_draw_payload_order/) proves that Crobat V followed by optional Dedenne-GX can preserve an important singleton more often than optional Dedenne alone, with higher Bench occupancy. This extension quantifies that tradeoff for one to four interchangeable targets, plus an information-only K0/K1 Prize-knowledge ablation.

Source program: [tools/bench_draw_target_multiplicity.py](../../tools/bench_draw_target_multiplicity.py). Independent [physical-card reproducer](reproduce.py).

## Exact state and assumptions

A valid seven-card opening contains Crobat V and Dedenne-GX retained in hand and another Basic Pokémon as Active. All k interchangeable target copies K are absent from the known opener and distributed among 53 originally unseen cards: one normal later draw, six Prizes, and 46 live deck cards. Known non-target hand plays have reduced the hand to h=5 while preserving both supports. Two Bench slots remain free.

Dark Asset draws a=max(0,7-h)=2 after Crobat leaves hand; Dedechange discards the remaining hand and draws six. The conditional Dedenne policy stops if a target is already in hand. The staged policy first uses Crobat if K is missing, then uses Dedenne only if K remains missing. No search, recovery, opponent effect, or useful discarded-K destination is modeled. Success is **at least one target copy retained in hand** when the policy stops.

## Combinatorial derivation

Let N=53, r=1 normal drawn card, p=6 Prizes, and k interchangeable target copies. The chance of zero targets among m selected positions is

\[
Q_k(m)=\frac{\binom{N-m}{k}}{\binom{N}{k}}.
\]

When the deck contains at least a+6 live cards, exact final-hand target retention is

- Conditional Dedenne: \`1-Q_k(r+6)\`.
- Conditional staged: \`1-Q_k(r+a+6)\`.
- Incremental staged reach: \`Q_k(r+6)-Q_k(r+a+6)\`.

In K0, when the player has not inspected the deck, expected Bench entries are \`Q_k(r)\` for conditional Dedenne and \`Q_k(r)+Q_k(r+a)\` for staged play. The expected extra staged Bench occupancy is therefore \`Q_k(r+a)\`.

In K1, a previous deck inspection can reveal that **all k target copies are Prized**, even though their face-down Prize positions are unknown. Let \`A_k=C(p,k)/C(N,k)\` for k<=p, zero otherwise. A K1 policy that values only K can decline futile draw support. Relative to K0, expected Bench entries decrease by A_k for Dedenne and by 2A_k for staged play. The extra staged Bench occupancy becomes \`Q_k(r+a)-A_k\`. K1 acquisition costs and any other benefit of drawing cards are omitted from this paired-state *information-only* comparison.

## Four-copy frontier

| Interchangeable K copies | Dedenne target reach | Staged target reach | Stage gain | Extra K0 Bench slots | All copies Prized |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 13.207547% | 16.981132% | +3.773585 pp | 0.943396 | 11.320755% |
| 2 | 24.891147% | 31.349782% | +6.458636 pp | 0.888970 | 1.088534% |
| 3 | 35.200205% | 43.464527% | +8.264322 pp | 0.836677 | 0.085375% |
| 4 | 44.272176% | 53.640912% | +9.368736 pp | 0.786477 | 0.005123% |

Over the one-to-four-copy range, the marginal success of staged draw increases with target multiplicity while its expected Bench occupancy cost decreases. Early Crobat draws more often hit a target, so the player can avoid a second two-Prize support body more frequently. All-Prized configurations also become much rarer.

For a hypothetical final-target value V and per-extra-occupant penalty C, the K0 stage preference threshold is \`C/V < (Q_k(r+6)-Q_k(r+a+6))/Q_k(r+a)\`. At h=5, it is 4.000% for one target and approximately 11.912% for four. This is a toy objective rather than matchup-derived Prize-exchange or win-rate evidence.

The usual four-copies-per-card-name limit applies to real Expanded deckbuilding, aside from rule exceptions. A larger k in the supplied program should be interpreted as a functional class containing different names, not five or six copies of an ordinary named card.

## Verification and limitations

The primary implementation evaluates exact fractions using binomial coefficients. The independent reproducer exhaustively chooses up to four target positions from small physically labeled card populations, constructs literal hands, Prize partitions, and ordered decks, then simulates Crobat and Dedenne transitions. It agrees for three starting draw widths, four multiplicities and both K0/K1 knowledge states. The k=1 case also matches the preceding singleton model exactly: staged success 9/53, Dedenne success 7/53, extra K0 Bench 50/53, extra K1 Bench 44/53.

Run \`python results/bench_draw_target_multiplicity/reproduce.py\` on Python 3.11+.

Limitations include conditioning on a specified opening, treating all K copies as strategically equivalent, excluding paid search and other card effects, ignoring the value of K in the discard pile, and not pricing gust/Knock Out liability realistically. A future model should allow heterogeneous target values and execute real hand mutations interleaved with Quick Ball payments.
