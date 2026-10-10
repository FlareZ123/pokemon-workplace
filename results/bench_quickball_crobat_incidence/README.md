# Opening material incidence for paid Crobat/Dedenne staging

## Motivation

The [paid Quick Ball, Crobat and Dedenne continuation](../bench_quickball_crobat_dedenne/) found a +6.020067 percentage-point advantage in final-hand singleton retention conditional on a precise five-card-hand state. This study measures how frequently that state can even be approached from a particular 60-card deck role composition. A conditional gain should be multiplied by the incidence of its setup requirements before it is interpreted as deck-level access improvement.

[Model](../../tools/bench_quickball_crobat_incidence.py) and [independent exhaustive physical oracle](reproduce.py).

## Deck and event definition

| Card role | Copies |
| --- | ---: |
| Dedenne-GX D, must be held in opener | 1 |
| Crobat V C, must remain in live deck | 1 |
| Non-Basic target singleton K, absent from opener | 1 |
| Quick Ball Q | 4 |
| Designated discardable cards F | 4 |
| Other ordinary starting Basics O | 4 |
| Neutral filler X | 45 |
| **Total** | **60** |

An accepted seven-card opening must include D, at least one Q, at least one F, and at least one O. Neither C nor K may be among the opener. O is chosen as Active. After the seven-card opening, the player sets six Prizes and takes one later natural draw. C must remain among the live deck cards, to be fetched by Quick Ball.

There are exactly six ordinary Basic Pokémon for opening validity: D, C and four O. The event treats opening Q/F/O copies jointly and never double-counts multiple alternatives.

## Exact combinatorial method

For q,f,o copies of Q,F,O in the opening, the remaining filler slots are 6-q-f-o. The count of qualifying labeled openings is

\[
H=\sum_{q=1}^4\sum_{f=1}^4\sum_{o=1}^4
\binom4q\binom4f\binom4o\binom{45}{6-q-f-o}.
\]

Impossible binomial terms contribute zero. The accepted-opening probability is

\[
P(A)=1-\frac{\binom{54}{7}}{\binom{60}{7}}.
\]

Conditioned on an eligible opener, C is a specified remaining card among 53, with 46 positions still in the live deck after six Prizes and one later draw. Consequently,

\[
P(M\mid A)=\frac{H}{\binom{60}{7}}\frac{46}{53}\bigg/P(A).
\]

## Results

| Event | Probability |
| --- | ---: |
| Ordinary Basic-valid opening | **54.143608%** |
| Required D/Q/F/O opening roles with C and K absent, unconditional | **0.316462%** |
| Above plus Crobat still live after Prize placement and natural draw, unconditional | **0.274666%** |
| Complete material event given a valid opening | **0.507290815%** |

The previous paid continuation gave a +6.020067 percentage-point K-retention difference at h=5 after preparatory hand plays. The product of that conditional advantage with **this exact opening material event** is **0.030539246 percentage points** of valid-opening target-access contribution under the stipulated continuation.

**Interpretation boundary:** This product presumes all material-positive hands can make legal non-K plays to reach h=5, preserve D/Q/F, and execute the named continuation. This study has verified material identities and opening/Prize/draw locations, while the playability of those additional hand-reduction actions remains unverified. The product is a conditional composition benchmark. It is neither the deck's total win-rate improvement nor a global upper bound on other Crobat and Dedenne uses.

## Verification and limits

The primary exact calculation sums multivariate hypergeometric opening combinations and then integrates C's joint Prize/draw location. An independent reproducer enumerates every labeled opening hand, every compatible Prize set, and every later draw in three small decks. All valid-opening, opening-material, full-material and accepted-conditional counts match as exact rational numbers.

Run \`python results/bench_quickball_crobat_incidence/reproduce.py\` from repository root with Python 3.11+.

The role composition is a controlled experiment. It assumes F is available for safe discard and leaves filler text unspecified. The model excludes another path to K, Item/Ability lock, matchup pressure, alternate starting Active decisions, opponent mulligan bonus draws, search for the connector, and real hand-play feasibility. The major finding is the scale discrepancy between an attractive conditional line and its restricted opening-material frequency.

## Executable seven-card first-turn baseline

The h=5 continuation above requires unspecified additional hand plays. A stronger narrower certificate can be obtained with **no discretionary hand-reduction actions**:

1. A valid opening contains Dedenne-GX, Quick Ball, at least one expendable F and another Basic O; Crobat and the non-Basic K are absent from the opening.
2. Choose an O as starting Active, keeping Dedenne, Q and F in hand. Do not Bench other Basics during setup.
3. Place six hidden Prizes. Draw the single normal card for the player's first turn. This leaves exactly **seven cards in hand**: seven-card opener less the chosen Active plus one turn draw.
4. If K is already in hand, stop. Otherwise either (a) play Dedenne, or (b) discard F to Quick Ball, fetch live Crobat, play Crobat to Bench, use Dark Asset, then conditionally play Dedenne if K remains missing.

The source Rulebook allows playing Basic Pokémon from hand onto Bench, as well as using Items and Abilities on a turn when their conditions are met. The model assumes no applicable Ability/Item lock and two free Bench spaces. For the staged line at h=7, **Dark Asset draws exactly one card**. Because the intended actions themselves reach the compared hand sizes, this certificate does not require a hypothetical filler-action sequence.

| Metric | Seven-card direct line |
| --- | ---: |
| Material event given Basic-valid opener | 0.507290815% |
| Dedenne-only conditional K retention | 13.210702341% |
| Quick Ball → Crobat → conditional Dedenne K retention | 15.384615385% |
| Conditional staged improvement | **2.173913043 percentage points** |
| Restricted material-weighted access contribution | **0.011028061 percentage points** |

The exact weighted increment equals `3395/30785103` as a probability, or approximately **0.011028061 percentage points**. These rates concern an explicitly restricted policy comparison, not the marginal contribution of Crobat across all possible opening hands and continuations.

An independent enumerator at [certificate.py](certificate.py) now proves the composition directly: a physically labeled 18-card toy enumerates every accepted opening, every Prize configuration, every natural draw, and averages all possible target positions in the untouched deck and after Quick Ball's shuffle. It agrees exactly with the product of the independent opening-incidence and support-continuation calculations. The 60-card regression checks the exact rational `3395/30785103` and the one-card Dark Asset draw.

This seven-card comparison provides a better established immediate-play baseline. The h=5 scenario remains useful as a sensitivity experiment for turns where a separately validated sequence has reduced the hand further. Both scenarios still assume the card role F can be discarded harmlessly and that the staged extra Bench exposure is acceptable; opponent interaction, card search competition and decklist optimization remain outside scope.
