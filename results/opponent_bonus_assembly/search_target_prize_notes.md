# A search connector can be playable while its singleton target is Prized

## Question

The earlier physical matching and payment-gated models check whether a
search source is drawn and its mandatory discards can be paid. A search
effect still needs the intended target to be in the deck. At K0, the
target may be Prized and unknown.

This exact extension isolates the search-target location issue.

## Model

Take N cards, H opening cards, P Prizes, B ordinary Basic starters and
exactly one non-Basic A target, one non-Basic B target, and one
single-output search card. Include D designated disposable cards and
neutral fillers. Condition on the opening having an ordinary Basic.
Draw m optional post-setup bonus cards. A two-unit payment is considered
feasible only if at least two designated disposable cards have been
observed in the combined hand.

The two goals can both be satisfied either when A and B are directly
in hand, or when exactly one is in hand and the search source is held,
has the two designated discards, and the missing other target remains
in the deck. This intentionally excludes drawing later, other sources,
retrieval from Prizes and any effect that can fetch two targets.

Let p_direct(m) be the probability both singleton targets are seen, and
p_search(m) the probability of exactly one target plus source and two
discards, all conditional on a legal Basic opener. These are calculated
exactly from the physical count-class distribution.

Given a target missing from the H+m observed cards, it must be one of
the N-H-m unseen physical cards. By exchangeability, exactly P of those
are Prize positions. Hence

    Pr(missing target still in searchable deck) =
        1 - P/(N-H-m).

The actual objective probability is therefore

    p_direct(m) + [1-P/(N-H-m)] * p_search(m).

A naive model that treats every unseen target as searchable reports

    p_direct(m) + p_search(m).

The overstatement is exactly

    P/(N-H-m) * p_search(m).

This is a rigorous Prize-obstruction correction conditional on the
specific route being otherwise possible.

## Worked sensitivity: 60 cards

With N=60, H=7, P=6, B=12 ordinary Basics and one card each of A, B
and the generic search source:

| Safe discards D | Bonus draws m | Naive access | Prize-aware access | Overstatement |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 0 | 1.077825% | 1.072114% | 0.005711 pp |
| 4 | 8 | 7.481669% | 7.235905% | 0.245763 pp |
| 8 | 0 | 1.237063% | 1.213326% | 0.023738 pp |
| 8 | 8 | 10.688023% | 10.014745% | 0.673277 pp |
| 12 | 0 | 1.465046% | 1.415499% | 0.049547 pp |
| 12 | 8 | 12.831332% | 11.872280% | 0.959052 pp |
| 20 | 0 | 1.996534% | 1.886818% | 0.109716 pp |
| 20 | 8 | 14.295621% | 13.141331% | 1.154290 pp |

The target's conditional Prize risk among unseen cards is 6/53 before
bonus draws. After eight observed bonus draws it is 6/45. This
increasing conditional obstruction can matter even while the absolute
hand-assembly chance grows from drawing more cards.

The row-level probabilities are unconditional over accepted opening
hands and random Prize placement. The risk fraction applies only to
the state branch where the target is missing and the search would
otherwise resolve both demands.

## Evidence

- [Exact calculation kernel](../../tools/opponent_bonus_search_target_prize.py)
- [Independent physical reproducer](search_target_prize_reproduce.py)
- [Shared CI](../../.github/workflows/validate-opponent-bonus-assembly.yml)

The reproducer exhaustively enumerates labeled opening hands, Prize
subsets and bonus-card draws for two small decks, tests the
Prize-ignorant and Prize-aware probabilities against the abstract
formula as exact fractions, and checks the 60-card sensitivity table.

## Limitations

This is a specific singleton route, not a full deck engine. An actual
search effect may be disabled, its source may be Prized, the required
discard cards may be worth retaining, and a player may have other
connectors or Prize recovery actions. Search is assumed usable after
the opponent has taken their optional bonus cards. Deck search and
accurate K1 Prize inference will change *future* decisions, but it
cannot retroactively make a Prized singleton searchable by an ordinary
deck-search effect.

Computer Search and Ultra Ball are motivating printed examples of
one-output effects with two-card discard costs; their actual search
domains differ. The abstract source is permitted to search either A
or B by construction. This preserves the limitation of the
mathematical claim.
