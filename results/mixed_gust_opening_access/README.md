# Mixed Boss and Counter Catcher opening access

## Question

Suppose the deck has a fixed total of four gust cards and allocates those slots between Boss's Orders and Counter Catcher. How often can it access any gust, a playable Boss during a Counter-closed Prize state, or both source classes by the first or second natural draw?

This is an **exact physical access** calculation for a 60-card hypothetical deck with B Basic Pokémon, seven starting cards conditioned on at least one Basic, and six face-down Prizes. Boss and Counter are both non-Basic. Card-use gates and sequencing are imposed only as labels on source availability.

## Source-class inclusion-exclusion

Define F(B,G,k) as the exact probability of at least one of G non-Basic source copies appearing in the accepted hand or first k natural draws, from [multi-copy opening access](../gust_copy_opening_access/). For b Boss copies and c Counter copies,

- Any source is visible with probability F(B,b+c,k).
- At least one Boss is visible with probability F(B,b,k).
- At least one Counter is visible with probability F(B,c,k).
- **Both types** are visible with probability F(B,b,k)+F(B,c,k)-F(B,b+c,k).

The [joint distribution tool](../../tools/mixed_gust_opening_access.py) independently enumerates the complete distribution over (Boss copies, Counter copies) seen, using an exact three-category multivariate hypergeometric opening followed by a two-category draw.

If Counter's Prize gate is closed, the model's immediately available gust-source probability is the Boss-only column. If its Prize gate is open, the immediately available source probability is the any-source column. This is a card-visibility and source-gate test; it excludes Supporter contention, Item locks, Target restrictions, other effects and search access.

## Four total gust slots after two natural draws

| Boss / Counter split | Any source, B=4 | Boss, B=4 | Both types, B=4 | Any source, B=16 | Boss, B=16 | Both types, B=16 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 / 4 | 45.7205% | 0% | 0% | 47.6811% | 0% | 0% |
| 1 / 3 | 45.7205% | 13.7947% | 4.5556% | 47.6811% | 14.5503% | 5.0544% |
| 2 / 2 | 45.7205% | 25.8946% | 6.0687% | 47.6811% | 27.2067% | 6.7322% |
| 3 / 1 | 45.7205% | 36.4815% | 4.5556% | 47.6811% | 38.1852% | 5.0544% |
| 4 / 0 | 45.7205% | 45.7205% | 0% | 47.6811% | 47.6811% | 0% |

For a fixed four-card package, initial **any-gust connectivity is unchanged** by the class split. Access under Counter's closed Prize gate increases as more slots become Boss. The 2 Boss / 2 Counter split maximizes the chance of seeing both categories among these five splits.

A deck needs to price the situations where each card is actually legal and useful. The joint-access probability cannot itself rank these five decks.

## Verification

[reproduce.py](reproduce.py) independently enumerates **64 complete labeled ten-card physical populations** with distinct Boss, Counter, Basic and filler card identities; varies source counts, Prize count and one/two natural draws. Every joint probability agrees exactly with the hypergeometric solver. Another 50 combinations cover five Basic counts, the first and second natural draws, and all five four-copy splits at T=60.

Run `python -m results.mixed_gust_opening_access.reproduce`. No sampling is used.

## Limits and next steps

This model assumes an accepted Basic-containing opener, uniform Prize and deck positions, no extra mulligan cards, no search/draw engines and a static four-card source package. It treats drawn Boss as an unconditional gust option and drawn Counter as an option only when its Prize gate is open; it has no opponent card actions, match-specific locking effects, or same-turn resource contention.

The appropriate next integration is to combine this mixed-source joint access vector with the [two-sided gust race](../opposing_counter_bench_window/) and source usage over multiple turns, rather than replacing that tactical model with a source-count score.