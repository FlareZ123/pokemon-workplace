# Exact critical decision weights for opposing Judge/Ace/no-reset policies

## Why calculate policy breakpoints?

The [two-objective opposing Supporter study](../beheeyem_opponent_self_target/) gives the opponent a four-copy hypothetical X target card and a narrow tradeoff between its own target readiness and preventing Beheeyem's next Mysterious Noise attack. It evaluates selected denial weights `lambda`, but an optimizer needs to know **where decisions actually change**, and whether a policy remains optimal throughout the interval between selected weights.

Each action's payoff for an observed opponent hand and Beheeyem first-packet route is

```text
U(action; lambda) = P(own X available after response)
                  - lambda × P(Beheeyem next packet | first packet).
```

Within a fixed observed hand, both terms are exact rational constants. Therefore `U` is affine in `lambda`. Among pass, Judge, and Ace Trainer, the best legal action is the upper envelope of up to three lines, which changes only at a **rational intersection**. Pairwise intersections are complete candidates, and retaining those where the actual global selected-policy metrics change produces an exact finite piecewise-constant policy frontier.

## Physical setup

We use four Beheeyem, four TAE, one Computer Search, and one T3 extra draw in the same established three-Basic conditional attacker model. The independent opponent deck has 12 Basics, four Ace Trainer, four Judge, four X and 36 filler; after a valid Basic-containing seven-card opening, two deck draws and `s` earned Prize cards are available. The opponent's hand, Prize totals and whether Beheeyem publicly used its singleton tutor on the first attack are the policy observations. Original unknown opponent Prize locations remain K0.

We calculate both **aggregate-route** policies (opponent does not condition on the publicly visible tutor usage) and **observed-route** policies (opponent conditions on direct first packet versus paid tutor rescue). The own-X and packet-access objective retains the [two-objective model's](../beheeyem_opponent_self_target/) assumptions and limitations.

## Complete exact frontiers for ten representative scenarios

The count in the last columns is the number of distinct open-denial-weight intervals with a fixed optimal policy and resource-outcome vector. Only strictly positive relevant thresholds are shown.

| Beheeyem Prizes r | Opponent Prizes q | Route visible? | Pairwise candidate thresholds | Actual optimal-policy intervals | First switch `lambda` | Last switch `lambda` |
| ---: | ---: | :---: | ---: | ---: | ---: | ---: |
| 0 | 6 | No | 1 | 2 | 3.367994 | 3.367994 |
| 0 | 6 | Yes | 2 | 3 | 2.979444 | 3.556751 |
| 1 | 6 | No | 2 | 3 | 5.448856 | 81.677800 |
| 1 | 6 | Yes | 7 | **8** | **3.847504** | 98.731704 |
| 2 | 6 | No | 5 | 6 | 20.632935 | 22.160244 |
| 2 | 6 | Yes | 7 | **8** | **6.292489** | 284.287148 |
| 2 | 5 | No | 5 | 6 | 20.653989 | 22.206731 |
| 2 | 5 | Yes | 7 | 8 | 6.298909 | 284.577231 |
| 2 | 4 | No | 1 | 2 | 20.689173 | 20.689173 |
| 2 | 4 | Yes | 2 | 3 | 6.309640 | 285.062009 |

The model exhibits **as many as eight distinct decision regimes** for one fixed deck setup when public first-tutor-route observation is used. Ignoring the route can collapse the same setup to as few as three regimes (r=1/q=6). Thus observing one publicly visible earlier Item play can expand the policy's actionable tradeoff structure.

The r=1/q=6 route-aware case has its first exact rational change at

```text
lambda = 800168127187301020206 / 207970721609353909375
       ≈ 3.84750373.
```

If the opponent does not observe the tutor use, the first change instead occurs at approximately **5.44885570**. These numbers express the chosen arbitrary relative weight between the opponent's X-readiness probability and Beheeyem next-packet probability. They are mathematical boundaries within the supplied model, not empirical dollar/prize win-value estimates.

As lambda increases along the frontier, own-X access and Beheeyem's two-packet access **both weakly decrease**. That monotonic tradeoff follows from upper-envelope optimization with a linear two-objective utility. The regression asserts this for every adjacent interval, with exact fractions.

## Method and verification

- [Breakpoints engine](../../tools/beheeyem_opponent_self_target_frontier.py) enumerates physical hand-category observation classes, legal action sets and the two possible public first-attack routes. It constructs every positive rational pairwise crossing of action utilities and evaluates one rational interior point in each interval with the existing exact [two-objective solver](../../tools/beheeyem_opponent_self_target.py).
- It merges consecutive candidate intervals only when their exact X-readiness, Beheeyem packet probability and pass/Judge/Ace action fractions match. This suppresses crossings between actions that are never actually optimal.
- [Regression](reproduce.py) independently re-evaluates every interval interior, checks conservation and neighboring-boundary continuity, compares the high-lambda result with a large finite penalty, and reports ten representative full frontiers. [CI run 38133656250 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133656250).
- Rational arithmetic avoids apparent thresholds introduced by floating-point ties; displayed six-decimal boundaries are rounded only for readability.

The output currently targets a fixed Beheeyem B4/TAE4/C1/d1 and hypothetical opponent B12/A4/J4/X4 deck. Future comparative optimization should test other resource counts, time horizons and real card-derived self-setup objectives rather than interpreting the chosen `lambda` as a strategic constant across matchups. Another promising direction is the K1 version: when the opponent has searched its deck, exact self-X Prize knowledge can change its preference for resetting an already-depleted hand.
