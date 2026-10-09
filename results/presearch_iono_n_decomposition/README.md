# A paid search can change the value of its own K1 information

## Question

A deck search may reveal exactly which useful outs are Prized, allowing a better informed choice between Iono and N. A zero-target Quick Ball can supply that observation, but playing it consumes the Quick Ball plus one discarded card. How should the **material thinning effect** and **information option value** be separated?

## Exact conditional model

The earlier [Prize-informed Iono/N policy](../prize_informed_iono_n_choice/README.md) defines the K0 distribution of deck outs and the exact conditional redraw success functions.

Define `V(H,R)` as the success rate of the optimal **fixed** Iono/N choice before inspecting the deck when the old hand contains H cards and R interchangeable outs. Define `A(H,R)` as the success rate if the deck-out count K is observed before choosing the Supporter.

If a pre-search consumes p old-hand cards, including r outs, and reveals K while otherwise retaining the same deck composition, then

- **Material/pre-payment shift:** `V(H-p,R-r) - V(H,R)`.
- **Information value after payment:** `A(H-p,R-r) - V(H-p,R-r)`.
- **Total modeled change:** `A(H-p,R-r) - V(H,R)`.

This is an algebraically exact decomposition of conditional immediate out-access probability. The search's payment changes the future decision problem. Accordingly, the information benefit calculated *before* paying may differ from the information benefit after paying.

For Quick Ball, p=2 represents the Item itself plus one other card. The card's constrained Basic-Pokémon search can choose zero results under the supplied advanced rulebook's deck-search rule, while physical deck inspection still reveals K1. This projection assumes the Item is legal, both Supporters remain accessible, their Supporter windows are open, the search shuffle is neutral to the original deck-order belief, and the paid cards are removed before either redraw.

## Witness A: information option value disappears after thinning

Take D=46 preexisting deck cards, P=6 hidden Prizes containing U=10 unknown-zone outs, H=5 old-hand cards containing R=1 out, d=6 Prize-draw cards and Q=2 opponent-hand cards.

| Policy | Expected at-least-one-out access |
| --- | ---: |
| No pre-search, best fixed Supporter | **74.232970%** |
| Spend two non-outs, best fixed Supporter | **75.841039%** |
| Spend two non-outs, inspect deck, choose optimally | **75.841039%** |

The two spent non-outs improve the immediate draw pool by **+1.608069 percentage points**. After this material change, N is optimal for every possible K=4..10. The incremental information value is **zero**. Before paying those two cards, the same K1 observation had positive gross value of +0.169011 pp.

If the payment instead consumes one useful out plus one non-out, the model's best fixed action remains Iono at 74.232970% and K1 observation again has zero incremental value. This equality concerns the immediate out-access endpoint; loss of a useful physical card can have major future consequences.

## Witness B: thinning and information both contribute

With D=46, P=6, U=6, H=10, R=1, d=6, Q=2, pay two non-outs:

- Material/pre-payment improvement: **+0.204495 pp**.
- Additional K1 option value after payment: **+0.274329 pp**.
- Total improvement: **+0.478824 pp**.

The same type of search-first play can therefore gain from two distinct mechanisms in some states and only one in others.

## Interpretation

A paid search does more than reveal information. The payment removes physical cards from the later shuffle-back pool, changing both success probabilities and which subsequent action is best. The value of an extra observation should be recomputed **in the post-payment state**. Adding a prepayment information bonus to a material-thinning benefit can double-count states or assign a benefit that vanishes after the action.

These results are not deck-wide consistency or win-rate estimates. They condition on the existence of both Iono and N as viable next Supporters, a payable and otherwise legal zero-output search, an exchangeable deck-order prior, and the useful-out classification. They also omit costs of losing the Quick Ball for later turns.

## Reproducibility

- `tools/presearch_iono_n_decomposition.py` returns exact Fraction-based baseline, postpayment fixed policy, postpayment information policy and nonadditive decomposition.
- `results/presearch_iono_n_decomposition/reproduce.py` independently evaluates short finite compositions and asserts the witness probabilities with exact arithmetic.
- `.github/workflows/validate-presearch-iono-n-decomposition.yml` performs standalone CI.

Next work: integrate physical Quick Ball legality and payment DCI with the transition kernel, then evaluate information against future turn options rather than assuming a fixed endpoint.
