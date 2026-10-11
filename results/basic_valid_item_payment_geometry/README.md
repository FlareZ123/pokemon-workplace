# A held discard-gated Item is not necessarily strategically payable

## Question

The [physically paid Quick Ball experiment](../physical_quick_ball_search_option/) assumed that a particular type of disposable filler was present. How much would the Item's real first-turn availability be overstated if that discard-resource gate were omitted?

Treat **Quick Ball** (swsh1-179) as the example of a legal paper-Expanded Item requiring one *additional* card from hand to play. We model the physical rule while imposing separate hypothetical constraints on which card is strategically acceptable to discard. The rule itself permits discarding a much larger range of cards; these payment policies express state-dependent preservation preferences.

## Exact Basic-valid snapshot

A 60-card deck has B=12 opening Basic Pokémon, Q=4 Quick Ball, F acceptable non-Item discard cards, and P=44−F other protected cards. Draw seven, require at least one Basic, choose one as Active, set six random Prize cards, then draw one normal turn card going second. There are seven cards in hand after the Active is set and before further plays.

Compare four observable hand events:

1. At least one Q is physically held.
2. Q is held together with at least one F, a **strict, highly selective** payment policy.
3. The player can pay from F **or a spare Quick Ball** (requires at least two Q in hand).
4. The player can additionally discard an **extra Basic Pokémon left in hand after choosing the Active**, assuming that extra Basic is disposable.

The fourth condition is a consciously permissive counterfactual. Bench requirements may make an extra Basic strategically protected. All other cards are protected in these policies.

## Closed-form holding and strict-payment theorem

For a category S of size s that is disjoint from the B Basic starters, the probability that no S card remains in hand after Basic-valid setup and the turn's natural draw is exactly

A(s) = [(C(60-s,7) − C(60-s-B,7)) / (C(60,7) − C(60-B,7))] × [(53-s)/53].

This follows by excluding S from the seven-card opener while requiring a Basic, followed by avoiding S on the one natural turn draw. The unknown six Prize cards can be marginalized by exchangeability; selecting a Basic as Active does not remove S cards.

Therefore:

- P(Q held) = 1 − A(Q).
- P(Q held and F held) = 1 − A(Q) − A(F) + A(Q+F).

The spare-Item and extra-Basic policies are computed by an exact four-category multivariate hypergeometric opening plus natural-draw distribution, always conditioning on a valid Basic. An independent exhaustive labeled-card validator confirms the formulas.

## Exact 60-card comparison

| Acceptable F cards | Q held | Strict Q+F payable | Allow spare Q as payment | Also allow extra Basic |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 42.738824% | 0% | 7.389055% | 28.421839% |
| 4 | 42.738824% | 16.753450% | 21.610384% | 34.953922% |
| 8 | 42.738824% | **27.619222%** | **30.693460%** | **38.788363%** |
| 12 | 42.738824% | 34.389431% | 36.249552% | 40.900909% |
| 20 | 42.738824% | 40.661646% | 41.232242% | 42.465840% |
| 28 | 42.738824% | 42.391235% | 42.514646% | 42.722583% |

With F=8, the Item is physically held 42.738824% of Basic-valid first-turn hands, but only 27.619222% contain one of the specifically disposable fillers needed for the strict policy. Conditional on holding Quick Ball, only **64.6233%** of those hands can pay under that selective policy. Counting spare Q as acceptable raises conditional payability to **71.8163%**; permitting a leftover Basic raises it to **90.7567%**.

Adding acceptable discard cards at fixed B and Q cannot reduce strict payability: one can couple the F categories by relabeling protected cards as disposable. The exact regression checked all 45 possible F counts from zero through 44.

## Reproducibility

- [Exact setup and payment geometry](../../tools/basic_valid_item_payment_geometry.py): closed-form avoidance/inclusion-exclusion, multivariate composition and three DCI-style payment policies.
- [Independent labeled-card enumeration](reproduce.py): checks **336** small deck/Basic/Item/filler/opening/Prize combinations by explicitly enumerating every Basic-valid opener, disjoint Prize placement and natural draw, including each payment policy. Pins all major 60-card examples and monotonicity.
- [Windows CI](../../.github/workflows/validate-agent2-basic-valid-item-payment.yml): Python 3.13.

The payability classes are model assumptions. Their purpose is to quantify how sharply strategic resource protection can change whether a technically accessible Item can be played. The analysis excludes fetching a Basic Pokémon, other actions and actual downstream prizes or attacks, so these numbers are neither match win rates nor deck-construction recommendations.
