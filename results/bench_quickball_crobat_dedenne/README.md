# Paid Quick Ball -> Crobat V -> conditional Dedenne-GX

## Motivation and source cards

The earlier [Crobat/Dedenne result](../bench_draw_payload_order/) assumes both support Pokémon already in hand. This study models the alternate line when **Crobat V is searched directly from the live deck by Quick Ball**, with its actual hand-card discard payment.

Card text anchors from the bundled pool: Quick Ball \`swsh1-179\` must discard another hand card to search a Basic Pokémon into hand; Crobat V \`swsh3-104\` has Dark Asset (draw until six when played from hand onto Bench); Dedenne-GX \`sm10-57\` has Dedechange (discard the rest of hand and draw six when played from hand onto Bench). The model uses the newer effective Quick Ball discard-and-search text, with a guaranteed expendable discard card.

[Exact probability program](../../tools/bench_quickball_crobat_dedenne.py) and [independent physical replay](reproduce.py).

## Restricted 60-card conditional state

The valid seven-card opening contains an ordinary Basic chosen as Active plus Dedenne-GX, Quick Ball and expendable card F retained in hand. **Crobat V is guaranteed in the live deck**, with no Prized or opening copy. The non-Basic singleton K is absent from the seven-card opener. Six cards are Prized, and the player draws one ordinary card. Known non-K plays then leave a hand of size h preserving Quick Ball, Dedenne, F and K when naturally drawn.

The 46-card live deck contains Crobat plus 45 other cards. K occupies one of **52** positions other than the guaranteed Crobat: one ordinary draw position, six Prize positions, or one of 45 live-deck positions.

Two observable policies are compared:

- **Conditional Dedenne:** if K is already held, stop. Otherwise bench Dedenne and discard the rest of the hand to draw six from 46 live cards, including the irrelevant Crobat.
- **Paid Quick Ball staging:** if K is already held, stop. Otherwise discard F to Quick Ball, search Crobat V into hand, inspect the remaining deck and shuffle. If K is now known Prized, stop in the goal-directed K1 policy. Otherwise bench Crobat, use Dark Asset and then bench Dedenne only when K remains absent.

The paid staged line assumes two free Bench slots, legal Abilities and Item use, and disposable F. Quick Ball opportunity cost, other useful cards drawn, and vulnerability of two-Prize support Pokémon are not assigned game utility.

## Exact calculation

Let r be ordinary earlier draws, p hidden Prizes, n live cards other than searched Crobat, and N=r+p+n. Here r=1, p=6, n=45, N=52. The Quick Ball line reduces the initial hand h by one net card after discarding QB/F and fetching Crobat, then by another upon Crobat's Bench entry. Dark Asset draws **a=max(0,8-h)**.

Provided n is at least a+6, exact final-hand K probabilities are:

- Dedenne alone: \`r/N + (n/N)*(6/(n+1))\`.
- Paid Quick Ball staged line: \`(r+a+6)/N\`.

The n+1 denominator in Dedenne's second term reflects the still-present Crobat in the draw pile. After Quick Ball fetches Crobat and shuffles, the stage's target K is drawn from n remaining live cards.

| Hand size h | Crobat cards drawn | Conditional Dedenne | Paid staged | Incremental access |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 4 | 13.210702% | 21.153846% | +7.943144 pp |
| 5 | 3 | 13.210702% | 19.230769% | **+6.020067 pp** |
| 6 | 2 | 13.210702% | 17.307692% | +4.096990 pp |
| 7 | 1 | 13.210702% | 15.384615% | +2.173913 pp |
| 8 | 0 | 13.210702% | 13.461538% | +0.250836 pp |

At h=5, exact Dedenne reach is **79/598**, paid staged is **5/26**, and the gain is **18/299**. The h=8 line draws nothing from Crobat but still weakly improves K access by removing one irrelevant Crobat from the deck. That tiny gain has a substantial unpriced opportunity cost.

## Physical payment, Bench debt, and K1

Quick Ball is consumed along with F in **51/52** worlds, because the player stops beforehand only when the normal draw already found K. Dedenne-only does not require this payment.

At h=5, the expected number of added two-Prize support bodies is:

| Policy | Expected Bench entries |
| --- | ---: |
| Conditional Dedenne | 51/52 |
| Paid staged, ignoring the information gained by Quick Ball | 99/52 |
| Paid staged, using K1 to skip known-Prized K | **87/52** |

Searching the deck physically gives K1 Prize **composition** knowledge, with no location information for face-down Prize cards. The information-aware policy avoids 12/52 expected support entries relative to the staged line that ignores the search result. Both have the same K-retention chance; Quick Ball and F were already consumed even if the player then realizes K is Prized.

## Verification

The probability program uses exact \`Fraction\` arithmetic. The independent reproducer builds physical hands and ordered decks, discards QB and F, searches out the specific Crobat card, moves it into hand, explicitly reorders/shuffles the remaining cards over each K position, benches support Pokémon and performs the two draw effects. It separately covers drawn-K and Prized-K cases. For several deck sizes and h=4..8, all measured probabilities, Bench occupancies, and paid Quick Ball/Dedenne usages agree exactly.

Run \`python results/bench_quickball_crobat_dedenne/reproduce.py\` from the repository root with Python 3.11+.

This is a **conditional, target-only** experiment, not a deck's real setup rate or win rate. Its search-out is guaranteed live and its discard cost is easy by assumption. It does not model whether another use of Quick Ball would be better, Item/Ability lock, secondary uses of drawn cards, matchup interaction, pickup, search alternatives, or the tactical value of the target in another zone.
