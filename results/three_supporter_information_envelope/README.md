# Three Supporter options can reverse the value of Prize information

## Finding

Earlier [binary information-gap research](../binary_choice_information_gap/README.md) measured the benefit of observing which cards are Prized before choosing Iono or N. Does introducing a third genuinely available Supporter necessarily increase that **observation premium**?

**No.** Adding an action cannot decrease the optimal informed expected outcome. The incremental benefit of observing the hidden state before choosing may decrease or increase. In tested card-text-grounded scenarios it can change from positive to zero, or from zero to positive.

## General finite-action theorem

For hidden states s with normalized probabilities p(s), a common finite feasible action set A, and scalar action payoffs u(s,a), define:

- Best fixed decision (K0): F = max_a E[u(s,a)].
- Best informed decision (K1): O = E[max_a u(s,a)].
- Information option value: V = O - F, always nonnegative.

Choose any K0-optimal action j, and let r_a(s) = max(0, u(s,a) - u(s,j)). Exact statewise regret is max over challenger regrets. Therefore:

**max_(a != j) E[r_a] <= V <= sum_(a != j) E[r_a].**

Taking expectation of the maximum gives the lower bound, since it is at least each individual regret. Bounding that maximum by the sum gives the upper bound. With exactly two actions, both bounds are equal and reproduce the [binary disagreement identity](../binary_choice_information_gap/README.md).

With three or more actions, summing separate pairwise information gains can double-count incompatible hidden states. The expected best action must be evaluated jointly, after accounting for source payments and feasible actions.

## Paper Expanded card texts and payoff

The bundled English card database contains the following relevant prints:

- **Iono** (sv2-185): puts both players' hands on their deck bottoms and conditionally draws each player's remaining Prize count.
- **N** (bw3-92): shuffles both hands into their respective decks and draws each player's remaining Prize count.
- **Professor's Research (Professor Magnolia)** (swsh1-178): discards the hand and draws seven cards.

All three are Supporters. The model offers one **counterfactual selectable Supporter action** in the same turn and assumes each named card is legally accessible and its effects can resolve. The old-hand counts exclude the particular Supporter card played.

The sole payoff is the probability that the **newly drawn hand contains at least one interchangeable useful out**. It omits the value of other cards retained or lost, disruption to the opponent, deck-out consequences, future turns, tactical locks and attacks. The result makes no claim about which Supporter is strongest in actual games.

The model includes D=46 old deck cards, P=6 hidden Prizes, U useful outs located somewhere in the deck plus Prizes, H other old-hand cards, R known old-hand useful outs, d=6 remaining Prizes for the redraw, and Q=2 opposing old-hand cards. Conditional on only U being known, the exact probability of K outs in deck is:

Pr(K=k) = C(D,k) C(P,U-k) / C(D+P,U).

For each K, an Iono draw samples up to d cards from the original deck; N samples d from the shuffled D+H cards with K+R outs; Research samples seven from the original deck. Exact handling of short decks also accounts for Iono drawing into previously bottomed cards.

Within this **immediate draw-hit endpoint**, Research weakly dominates Iono when d is six or fewer, because its seven-card draw samples the same old deck as Iono's at-most-six-card draw. Opponent disruption, protection of hand-held resources and later game value are absent from this comparison.

## Two opposite witnesses

Percentages below are exact combinatorial probabilities rounded to six decimals, conditional on these constructed states.

| Hidden outs U, old hand H/R | Options | K0 best fixed | K1 adaptive | Incremental K1 value |
| --- | --- | ---: | ---: | ---: |
| U=10, H=5, R=1 | Iono / N | 74.232970% | 74.401981% | **+0.169011 pp** |
| U=10, H=5, R=1 | Iono / N / Research | 79.834498% | 79.834498% | **0** |
| U=3, H=8, R=1 | Iono / N | 35.602881% | 35.602881% | **0** |
| U=3, H=8, R=1 | Iono / N / Research | 35.791855% | 36.511525% | **+0.719670 pp** |

In the U=10 three-action case, Research wins at every feasible K=4..10, so perfect knowledge of K has zero incremental action-choice value. In the U=3 three-action case, K1 selects N at K=0,1,2 and Research at K=3, creating an observation premium absent from the Iono/N pair.

These values measure conditional access probabilities, **not deck consistency or win rates**.

## Paying for information changes the frontier

For U=3, H=8, R=1, suppose a legally usable deck-search action takes no searched card, spends two old-hand non-outs, reveals K, and shuffles an exchangeable deck. This is an *exogenously gated action*, not a claim that the required source and discard targets are physically present in every hand.

Relative to the optimal fixed no-search policy:

- Physical payment/thinning changes the best fixed redraw value by **+0.987185 percentage points**.
- The additional option value of learning K *after that payment* is **+0.050017 percentage points**.
- Total modeled improvement is **+1.037202 percentage points**.

Before paying, K1 information had +0.719670 percentage points of conditional value. Its premium shrinks substantially after the two non-outs are removed. If the payment consumes one hand-held useful out plus one non-out, the modeled immediate-access change and K1 switching gain both become zero. Future loss of that physical out is still consequential but unpriced here.

The correct decomposition is the payment-induced change in the best fixed policy **plus** the information value recomputed after payment. Adding prepayment information value to postpayment outcomes is generally incorrect.

## Reproducibility and next steps

- [Exact generic envelope](../../tools/multi_action_information_envelope.py) computes rational action means, an optimal fixed action, state-contingent choices, option value, and challenger-regret bounds.
- [Three-Supporter composition](../../tools/prize_three_supporter_choice.py) reuses the existing Iono/N payoff and exact hypergeometric Prize prior and adds Research's printed seven-card effect. Its paid-search variant always pays before observing K.
- [Reproducer](reproduce.py) checks **3,645** three-action two-state rational configurations against independent fixed/informed maxima and against the existing binary information-gap implementation. It separately exhausts **2,660** small physical Prize/subset/redraw cases and pins the stated large-deck witnesses.
- [Windows CI](../../.github/workflows/validate-agent2-three-supporter-envelope.yml) validates the same reproducer with Python 3.13.

Future refinements should add legal Supporter access probabilities, actual Quick Ball or Ultra Ball in hand, state-dependent discard targets, opponent objectives and multi-turn reward. A multi-action envelope can express those richer outcomes without rewarding an unusable theoretical search route.
