# Opening-hand displacement changes Grand Tree chain access odds

## Question

If the chosen Basic Pokémon is already in the opening seven-card hand,
what is the exact probability that at least one Stage 1 and one Stage 2 copy
remain in the searchable deck after both the rest of that hand and the six
Prizes have been dealt?

Grand Tree (`sv7-136`) can search the deck for a Stage 1 and conditionally
a Stage 2 during one effect. A Stage 1 or Stage 2 card in hand or Prize cannot
be picked by this particular **deck search**. A Stage 2 in hand may support
different lines, which are outside this calculation.

## Sample space and assumptions

Condition on one *designated* Basic Pokémon already occupying one of the
seven opening-hand slots. Exactly 59 other cards are uniformly randomly
partitioned as:

- 6 additional cards in the opening hand;
- 6 face-down Prize cards;
- 47 cards in the deck.

The 59 contain `a` Stage 1 copies, `b` Stage 2 copies, and
`59-a-b` other cards. Stage 1 and Stage 2 card families are disjoint.
This is a **setup-zone availability baseline** before any further draw,
search, discard, recovery, or shuffling. Grand Tree cannot actually evolve a
Basic during its player's first turn; this static baseline does not
represent the probability of an executable first-turn line or full later-turn
setup. Other Basic Pokémon, starting-player constraints, Grand Tree access,
deck legality, and opponent interaction are not modeled.

## Exact result

Write `u=hand+prizes=12` inaccessible cards and `N=59`.
For `a,b >= 1`, inclusion-exclusion gives:

```text
P(both stages accessible in deck)
 = 1 - C(u,a)/C(N,a) - C(u,b)/C(N,b)
     + C(u,a+b)/C(N,a+b).
```

Here `C(n,k)=0` for an impossible selection. Independent weighted
enumeration of hand and Prize partitions in
`tools/grand_tree_initial_zone_probability.py` reproduces the formula.

| Stage 1 copies | Stage 2 copies | Both in deck | Stage 1 only | No Stage 1 in deck |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 63.1794% | 16.4816% | 20.3390% |
| 1 | 2 | 76.4804% | 3.1807% | 20.3390% |
| 2 | 1 | 76.4804% | 19.6622% | 3.8574% |
| 2 | 2 | 92.3940% | 3.7486% | 3.8574% |
| 3 | 3 | 98.6486% | 0.6747% | 0.6767% |
| 4 | 4 | 99.7825% | 0.1093% | 0.1083% |

The three exclusive columns partition the possible zone outcomes.
"Stage 1 only" means a Stage 1 remains in deck but no Stage 2 does,
and refers only to what Grand Tree itself could obtain.

### Singleton decomposition

For `a=b=1`, the two cards must land among the 47 searchable deck
positions within the other 59 cards:

`P(full chain) = (47/59) * (46/58) = 1081/1711 = 63.179427%.`

The total probability of a usable Stage 1 is `47/59 = 79.661017%`.
The Stage 1-only outcome is `282/1711 = 16.481590%`.
No Stage 1 remains in deck with probability `12/59 = 20.338983%`.

Conditional on Stage 1 being in the deck, the singleton Stage 2 is in:
the 46 other deck positions with probability `46/58`, the six
remaining hand positions with probability `6/58`, or the six Prize
positions with probability `6/58`. Thus the event of Stage 1 in deck and
Stage 2 Prized has probability `141/1711 = 8.240795%`.

A calculation that conditions on *neither evolution card* being among
the other six hand cards and models only the six Prizes instead yields
`(47*46)/(53*52) = 78.447025%`. The conditioning differs; the
15.2676-percentage-point gap illustrates why initial-hand displacement
matters for deck-only effects.

## Reproduction

`python results/grand_tree_initial_zone_probability/reproduce.py`

The reproducer verifies the exact singleton rational probabilities,
enumerated normalization, independent inclusion-exclusion across all
16 copy-count pairs from one through four, zero-copy edge cases,
and the hand-then-Prize conditional factorization.

## Strategic interpretation

At initial setup, a search-chain's available deck resources depend on
where cards landed among hand, Prizes, and deck. Additional copies can
greatly raise the chance that each required stage remains searchable;
a singleton at either level can remain the bottleneck. These numbers
should not be interpreted as overall Grand Tree activation probability,
turn-two evolution probability, or evidence of an optimal deck count.

A subsequent search exposes more information about the remaining deck
and therefore Stage 2 availability (the human research document's
K0/K1 distinction). Modeling the timing and value of that information
requires a sequential decision model in addition to this zone prior.

## Confidence

Exact combinatorial result conditional on the clearly defined initial
partition model, cross-checked by two independent computations.
