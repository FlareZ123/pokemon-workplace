# When a powerful multi-output search is too expensive

## Physical setup and decision

The [bundle-choice engine](../../tools/opponent_bonus_output_bundles.py)
models one-use actions that can produce one or several named output categories.
Its [physical enumerator](bundles_reproduce.py) validates alternative
choices and simultaneous outputs against labeled card hands, hidden Prizes and
bonus draws.

A separate [payment-gated model](../../tools/opponent_bonus_bundle_payment.py)
takes a 60-card deck, a legal seven-card opening conditioned on twelve
unrelated ordinary Basic starters, and six Prizes. The strategic demands are
A and B. There are two A-only physical source cards, two B-only cards, and
two flexible sources capable of satisfying *either* goal once.

Compare one additional physical card in the same deck slot:

- **Bundle:** one card supplying both A and B, playable only when three
  distinct, designated safe-discard cards are also in the observed hand.
- **Single-output:** one additional flexible card supplying A or B once,
  with no modeled payment.

There are D designated safe-discard cards in the deck. Other cards are
protected or unusable as payment for this particular evaluation. The
remaining deck slots are neutral filler. This is an abstract comparison
of immediate goals satisfiable by physical source cards in the opening
hand, before actual effects, search targets, or tempo are considered.

## Exact results

| Designated safe-discard copies | Paid bundle joint completion | Third flexible card joint completion | Bundle advantage |
| ---: | ---: | ---: | ---: |
| 3 | 10.991815% | 15.179735% | -4.187921 pp |
| 4 | 11.005000% | 15.179735% | -4.174735 pp |
| 6 | 11.070618% | 15.179735% | -4.109117 pp |
| 8 | 11.205973% | 15.179735% | -3.973762 pp |
| 12 | 11.736856% | 15.179735% | -3.442879 pp |
| 16 | 12.636735% | 15.179735% | -2.543000 pp |
| 20 | 13.860667% | 15.179735% | -1.319068 pp |
| 24 | 15.303269% | 15.179735% | +0.123534 pp |
| 28 | 16.822301% | 15.179735% | +1.642566 pp |

The bundled action wins this model only when the designated safe-discard
pool is unusually large: the first tested winning count is D=24, while
D=20 is still worse. This isolates a mechanism described in
`resources/human_concepts.md` as state-dependent discardability and
active-move realism. The number of disposable cards can matter more than
the width of the printed search.

There is an unconditional ideal-bundle upper bound. The bundle can supply
both channels whenever drawn, yielding 21.085813% joint opening completion
for the underlying A/B/flexible/one-bundle source counts. Replacing the
bundle with a third one-output flexible card yields 15.179735%. The
payment-free upper bound overvalues the bundle when the real hand has too
few safely discardable cards.

## Methodology and verification

The exact grouped state has card-count classes for ordinary Basics,
A-only, B-only, flexible single-output, singleton bundle, safe-discard
fodder, and protected filler. Each observed `H+m` class-count vector is
weighted by the hypergeometric union probability and by the conditional
valid-Basic-opener factor. Prize positions are marginalized by
exchangeability. The objective succeeds when distinct physical A/B/flexible
cards can be matched to the goals, or when the bundle is present with
at least three designated disposable cards.

[The reproducer](payment_reproduce.py) uses independent labeled-card
opening, Prize and bonus enumeration in two small decks, asserts
exact rational equality, checks that payment-free output-bundle results
agree with the independent bundle engine, and reproduces the 60-card
sensitivity table. [GitHub Actions](../../.github/workflows/validate-opponent-bonus-assembly.yml)
runs this test with the other opponent-bonus regressions.

## Interpretation limits

The model treats every designated fodder card as immediately disposable,
regardless of matchup or later opportunity cost. Conversely, all other
cards are protected. A real deck can have complex state-dependent
discardability; some players will spend a formerly protected card in a
decisive turn. Search target availability, Supporter contention, Item
lock, card legality, targets Prized or otherwise unavailable, Bench
capacity, and subsequent sequencing are deliberately omitted.

The *printed* Secret Box is a useful motivating example because it
requires three other cards discarded to obtain several category-specific
outputs. This model only represents a generic two-goal bundle with a
three-card safe-payment gate. It does not compute Secret Box's actual
four-category gameplay or claim a competitive card-swap recommendation.
