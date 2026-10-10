# Exact Switch-access deadline in a symmetric six-Prize endgame

## Research question

How many copies of Switch does a defender need to increase the number of attacks required to win, given a uniformly randomized, finite defender draw pile and a fixed tactical deadline? This isolates the *availability* contribution of a card that has already been shown to have large conditional value in [the two-sided stochastic gust/escape analysis](../two_sided_stochastic_escape/).

## State and theorem

The opponent has exactly three identical Pokémon, each worth three Prizes and each requiring `h >= 1` further attacks to Knock Out. One is Active and two are Benched. The attacker needs six Prizes (two KOs) and cannot gust. The opponent may play any number of already drawn Switch Items, using at most one between consecutive attacker turns, and can choose new Active Pokémon after a KO. Both players have enough inert draw cards to complete the endgame. No other Trainers, Energy payments, normal Retreat, healing, Pokémon replenishment or opponent attacks are available.

The defender draw pile has `D >= 3h-1` cards, of which `S` are Switch and `D-S` inert; `0 <= S <= D`. The defender draws once between consecutive attacks; the earliest a Switch can be used is after the first attack.

**Exact theorem:**

`E[h,D,S] = 2h + (h-1) * [1 - C(D-(2h-1),S)/C(D,S)]`

with the ratio taken to be zero if `S > D-(2h-1)`.

The formula measures the minimum attacker's expected attack count against an opponent optimally using its drawn Switch cards. For `h=1` Switch is immaterial. For `h>=2`, only the event that at least one Switch is drawn in the **first `2h-1` defender draw steps** matters. The access probability is hypergeometric.

### Why the threshold and ceiling are exact

With no usable Switch in this window, the attacker naturally completes the two KOs in `2h` attacks. If at least one Switch becomes available in the first `h-1` defender draws, the defender can retain it until the first target has taken `h-1` hits, then move that nearly-KO target away. The two untouched targets each still require `h` attacks, forcing `3h-1` attacks total.

If the first Switch arrives between defender draws `h` and `2h-1`, the attacker has completed one natural KO. The defender can retain Switch until the second target has taken `h-1` hits, then move it away and require the entire `h` hits on the remaining target. Again the total is `3h-1`.

There is a matching universal ceiling of `3h-1` attacks: immediately before an attacker has won, at most one defending Pokémon may already be Knocked Out, and either remaining Pokémon can survive at most `h-1` hits. An additional successful hit achieves the second KO no later than `3h-1`. Multiple Switch copies cannot exceed this ceiling in the stated fixed board. A Switch arriving after defender draw `2h-1` misses the last opportunity to increase attack count. Thus a single timely Switch is sufficient, regardless of how many other Switches may subsequently be drawn.

## Exact numerical examples

For a 12-card defender draw pile:

| Hits per Pokémon | 0 Switch | 1 Switch | 2 Switch | 3 Switch | 4 Switch |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 4 | 17/4 | 49/11 | 254/55 | 261/55 |
| 3 | 6 | 41/6 | 81/11 | 169/22 | 778/99 |

For `h=3, D=12`, two Switch increase required expected attacks from six to `81/11 = 7.363636...`. The maximal delay available through timely Switch is two additional attacks, and each extra copy improves the chance of drawing at least one in time.

The marginal benefit of the `S`th Switch copy is `(h-1) * [C(D-k,S-1)/C(D,S-1)] * k/(D-S+1)`, with `k=2h-1`, interpreted as zero when the binomial numerator is impossible. Successive marginal benefits weakly decrease because the ratio of consecutive increments is `(D-k-S+1)/(D-S)` while the numerator is nonnegative. This captures duplicate-copy diminishing returns under this controlled access window; it does not decide real deck-slot allocation where additional copies could be discarded, searched, or used for other purposes.

If an ongoing Item lock prevents Switch throughout the game, the expected count remains `2h` for all tested `S`. Card type is verified against the bundled `sv1-194` Switch printing. The paper advanced rulebook's Item and switching clauses determine the intended mechanical distinction.

## Verification

[`reproduce.py`](reproduce.py) checks the theorem as an exact `Fraction` against the independent previously established two-sided draw/decision engine in **90 configurations**, with `h=1..6`, three defender deck sizes per `h`, and `S=0..4`. It verifies each corresponding Item-lock ablation.

A separately coded complete physical-order defender strategy oracle enumerates **1,712** concrete Switch-copy position sets across 16 `(h,D,S)` cases. In every case it independently confirms the exact dichotomy: outcome `2h` when all Switch copies miss the first `2h-1` positions, and `3h-1` otherwise. Its calculated mean matches the formula. Full future draw-order knowledge does not change optimal action timing in this particular homogeneous/no-Boss setting, unlike the [earlier asymmetric stochastic Retreat counterexample](../stochastic_retreat_payment_bridge/).

- [Reproduction and physical oracle](reproduce.py)
- [Underlying chance/minimax engine](../../tools/two_sided_stochastic_escape.py)
- [CI workflow](../../.github/workflows/validate-switch-access-window.yml)

This result is an exact game-tree property of a deliberately stylized opponent board. It is not a metagame estimate. Future work should introduce finite Bench mobility, costed Retreat, item suppression that changes between turns, and opposing gust. Adding attacks with different KO rewards or durability can invalidate the simple single-window theorem.
