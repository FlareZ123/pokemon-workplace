# Multi-out payment frontier before shuffle-back redraw

## Research question

When an upcoming full-hand return-and-redraw shuffles cards back into the deck, a prior search/Item may spend cards that would otherwise return to the draw pool. The earlier [destination model](../hand_destination_reset_geometry/README.md) modeled one target card. What if many cards are strategically interchangeable outs, some originally in the hand and some in the deck?

## Exact result

Set N = original deck size; H = old-hand size after removing the reset source; K = outs already in the deck; R = outs in the hand; P = distinct hand cards spent by a preceding action; r = outs among those P spent cards; d = fixed draw count. Assume an exchangeable deck after returning the hand, no intervening effects, and an objective of drawing at least one of these interchangeable outs.

Let L=N+H and T=K+R. The probabilities are:

- Baseline return-then-draw: **1 - C(L-T,d)/C(L,d)**.
- Pay before return-then-draw: **1 - C(L-P-(T-r),d)/C(L-P,d)**.

When an impossible failure combination is requested (fewer than d non-outs), its failure probability is zero. The model caps draws to the available pool size. The exact delta is second probability minus first probability.

These are hypergeometric *one-draw-step* probabilities conditional on preselected zones and paid-card identities. They do not measure winning or full action-line success.

## Verified 60-card-shaped witness

Use N=46 original deck cards, H=5 old-hand cards, d=6 draws, P=2 paid cards, and eight interchangeable outs total (K=7, R=1).

| Pre-reset payment | Probability of >=1 out | Change from no payment |
| --- | ---: | ---: |
| No prior payment | 66.148600% | Baseline |
| Pay two non-outs | 67.845771% | **+1.697171 pp** |
| Pay one out and one non-out | 62.486733% | **-3.661867 pp** |

The same literal two-card payment therefore has opposite signs in immediate draw accessibility depending on its composition.

With the same N, H, P and d and exactly one hand out, a payment that spends one out remains harmful to at-least-one-out exposure through T=24 total outs. Its delta becomes positive at **T=25**, where the gain is only **+0.011920 pp**, as the shrunken pool slightly outweighs one removed target. This reversal occurs near draw-success saturation and is a mathematical boundary rather than an argument to sacrifice important game resources.

## Two useful inequalities

Under this one-step model:

1. **Only non-outs are paid** (r=0): pay-first cannot reduce immediate at-least-one-out exposure. Removing only non-outs weakly improves target density.
2. **All paid cards are outs** (r=P): pay-first cannot increase immediate at-least-one-out exposure. Removing only outs weakly reduces target density.

Mixed payments need the exact hypergeometric comparison; their sign can change with the number of outs, draw count, and old-hand size.

This provides a concrete probabilistic representation for a narrow DCI question: *the immediate opportunity cost of a payment depends on its membership in the current objective's useful-out set*. The same card can change membership when matchup, turn plan, or discard payload changes.

## Reproducibility

- `tools/hand_return_payment_frontier.py` computes exact rational probabilities and validates deck/hand/payment feasibility.
- `results/hand_return_payment_frontier/reproduce.py` verifies **3,556** exhaustive labeled small-state cases against independent combinations, including all feasible payment compositions in the checked ranges, and guards the numerical thresholds.
- CI workflow: `.github/workflows/validate-hand-return-payment-frontier.yml`.

## Scope and limitations

The pre-action is modeled solely as payment removal; the model does not price any search output, K1 observation, deck shuffle before the hand return, action timing, lock status, or broader resource reuse. Declaring multiple outs interchangeable is an explicit conditional objective: true utility may differ strongly among those cards. This is a targeted local continuation of the destination project, not a recommendation for a specific competitive deck.

Next: incorporate sequential search policy and future utility after return-and-redraw, so the immediate accessibility improvement can be compared with lost access to the paid cards on later turns.
