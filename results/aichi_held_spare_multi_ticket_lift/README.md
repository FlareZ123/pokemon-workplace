# Aichi paid-spare thinning with one to four Ticket copies

## Question

The [singleton Ticket census](../aichi_held_spare_ticket_lift/)
found a tiny maximum first-Stellar-Wish improvement from
a legal Guzma & Hala paid search for spare TM: Evolution
and Jet Energy, conditional on a restrictive natural
Jirachi/G&H first-turn hand.

The Aichi experimental Ticket package research also considers
multiple Ticket-role Item slots. Does the tiny incremental
gain simply scale linearly with the number of Tickets?

## Exact opening and Prize model

The published Aichi Vileplume source roster has four
first-turn-neutral Supporter TechSlots. Reinterpret `q`
of those slots as **Ticket-role Items**, where
`q=1..4`, preserving a 60-card deck and the remaining
source card counts.

Condition on a Basic-valid seven-card opener. Count
only deals where Jirachi is among those seven, G&H is
naturally held by the one normal draw, exactly one
TM: Evolution and one Jet Energy are visible, the
spares are in the searchable deck, at least one
Artazon is searchable, and **no Ticket is already
in hand**. Among the `q` unseen Tickets, any
may be Prized and `k` may remain searchable.

For every `k=0..q`, compute the exact accepted-opening
mass using the multivariate hypergeometric source/Prize
partition, and then multiply by the direct Wish access
difference when the G&H optional search removes
two **non-Ticket** cards. The post-G&H decks have 45
(no payment) and 43 (paid duplicate fetch) cards.

Given `k` searchable Ticket copies in `N` cards,
an unused Stellar Wish observing five shuffled cards
sees at least one Ticket with probability

`1 - C(N-k,5)/C(N,5)`.

This is a visibility/access-to-one-Ticket measure.
A single Stellar Wish still selects **only one**
of the five viewed cards, and this model ignores
a separate Map requirement for later Prize resets.

## Exact optimistic ceilings

| Ticket copies `q` | Maximum added direct Ticket sighting across Basic-valid starts |
| ---: | ---: |
| 1 | **+0.0005687710 pp** |
| 2 | **+0.0009622162 pp** |
| 3 | **+0.0012165057 pp** |
| 4 | **+0.0013620095 pp** |

The fractions preserved in the
[reproducer](reproduce.py) are respectively

- `111113/19535630400`;
- `524926447/54553899079680`;
- `15595805891/1282016628372480`;
- `3118069277/228931540780800`.

Within this **specific natural-route opening model**, the
bound rises with Ticket copies and exhibits sharply
decreasing marginal improvements. Four Ticket slots
produce only about **2.395 times** the singleton
direct thinning benefit.

The probability of the required natural source event
with **no Tickets already held** also changes with
`q`, so this is a conditional distribution result.
It cannot be obtained by multiplying the single-copy
effect by `q`.

All figures are optimistic upper bounds on a single
direct first-Wish Ticket-visibility channel. They assume
the two G&H payment cards are strategically expendable,
all three searches can be executed, and Jirachi is
still Active with an unused usable Ability. Matchups
and support-resource contention can make the actual
gain smaller or entirely absent.

## Independent validation

Calculation:
[tools/aichi_held_spare_multi_ticket_lift.py](../../tools/aichi_held_spare_multi_ticket_lift.py).
Physical oracle: [reproduce.py](reproduce.py).

Four smaller source decks are exhaustively enumerated
by Basic-valid opener, disjoint Prize selection and
one normal draw. Each literal physical state is sorted
by exactly how many Ticket copies remain searchable.
The resulting per-`k` masses match the analytic
partitions. A separate top-card-subset oracle checks
the multiple-Ticket hypergeometric probability.
The full Aichi fraction for `q=1` must reproduce
the independent singleton Ticket experiment exactly.

## Limitations

The synthetic Ticket replacement may change the
deck's competitive viability and endgame Supporter
suite. A two-Ticket/one-Map Prize-reset package
has distinct action and timing requirements;
this analysis deliberately does not grant an
extra Map, a second Jirachi activation, or
access to a second Ticket from the same Wish.
It should not be read as a tournament
win-rate increment or a justification for
four Ticket copies.

Earlier Tag Call, initial Stellar Wish before
G&H, Town Map and Prize exchanges, discard
recovery, and multi-turn control interactions
are outside this natural-route visibility
ceiling. Those effects remain important in
full Aichi game modeling.
