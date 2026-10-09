# Extra Quick Ball versus actual discard payment in turn-one Gothitelle setup

## Question

After requiring four ordinary Basic Pokémon plus Gothita on the
turn-one board, what is the value of a second Quick Ball for hands
missing **two** Basic pieces? What does its separately payable
discard cost do to the exact two-turn access event?

This extends [`gothitelle_core_board_joint_access`](../gothitelle_core_board_joint_access/)
with a disjoint category of explicitly approved disposable cards. One
Quick Ball **must** discard Sky Field. If a second Quick Ball is needed,
it must also be present by the end of turn one's natural draw, and
another disposable card must remain in hand to pay for it.

- Engine: [`tools/gothitelle_two_quick_joint_board.py`](../../tools/gothitelle_two_quick_joint_board.py)
- Independently labeled SFT: [`reproduce.py`](reproduce.py)

## Mechanics and policy

Initial opener: seven cards with an ordinary Basic Pokémon to serve
as the initial Active. Six random Prizes are set, and a natural draw
occurs on turns one and two.

The objective at the end of turn one is to hold/establish four
ordinary Basics (one Active, three Bench) **and Gothita** (fourth Bench),
having discarded Sky Field via Quick Ball. Gothitelle plus Rare Candy
must be available after turn two's natural draw.

Exactly five disjoint first-turn action classes are counted:

1. All needed Basics naturally seen: pay Sky with one Quick; restricted
   search can select no target.
2. One missing ordinary Basic: search it with Sky-paying Quick.
3. Missing Gothita only: search it with Sky-paying Quick.
4. Two missing ordinary Basics: use two Quick Balls, paying Sky and
   a separately approved disposable card.
5. One missing ordinary Basic plus missing Gothita: use two Quick
   Balls, paying Sky and the disposable card.

These use the same physical Bench limits. Two searches remove two
unprized Basic cards and leave a smaller turn-two deck. Probability
calculation sums the **joint Prize distribution of Gothita and ordinary
Basics** before evaluating the remaining evolution card outs. Only
hands containing both required Quick Balls and the second payment
may take the double-search branch.

## Exact illustrative example

Disjoint 60-card partition: 3 Gothita, 2 Gothitelle, 4 Rare Candy,
8 ordinary Basics, 4 Quick Ball, 2 Sky Field, 12 other independently
approved discard cards, 25 other filler. The disposable class replaces
filler without changing the other counts.

| Branch | Per seven-card opening attempt |
| --- | ---: |
| No Basic search needed | 0.000020203% |
| Search the fourth ordinary Basic | 0.001097614% |
| Search Gothita | 0.000455535% |
| Search two ordinary Basics | 0.000152073% |
| Search one ordinary Basic and Gothita | 0.000101286% |
| **One Quick budget** | **0.001573353%** |
| **Up to two Quick Balls** | **0.001826711%** |

The second paid search contributes **0.000253358 percentage points**,
or approximately **16.1031% relative** to the one-Quick baseline,
within this restricted population.

Changing only the approved-discard/filler partition produces:

| Approved discard copies | Gain from second Quick (percentage points) |
| ---: | ---: |
| 0 | 0 |
| 4 | 0.000084453 |
| 8 | 0.000168906 |
| 12 | 0.000253358 |
| 20 | 0.000422264 |

**The gain is exactly linear in approved-discard count here.**
Every successful second-search state needs two Quick copies, Sky Field,
one disposable payment, two or three core Basics and at least one
evolution piece among just eight observed cards. Consequently only
one disposable card can fit into that observed hand in successful
double-search states. Replacing filler with additional approved
discards increases that one-card event mass linearly. This does not
generalize to larger draw windows or multi-card payment costs.

## Evidence and limits

Two independent, label-level, physical-copy enumerations exhaust
12- and 13-card small populations, including Prize placement, both
searches, the resulting physical draw deck and individual branch
masses. All five analytic fractions agree exactly. A zero-Prize
control, zero-approved-payment invariant, one-Quick limit and
linearity regression extend the test.

The two searches are assumed usable as Items on turn one and their
second cost is payable from a separate card already deemed
strategically disposable. The abstraction excludes searching for
either Quick Ball, drawing extras via other effects, accessing the
later two entrant Basics, opponent Item lock/KO, realistic individual
Basic names, and the opportunity cost of those disposable cards.
The Collapsed Stadium/Ninetales board conditions are still supplied
as in the earlier deterministic two-turn witness.

These are deliberately narrow probability statements about **joint
card access and timed Bench assembly**, not a deck win percentage
or an argument for playing four Quick Ball in a particular list.

## Next question

Include one search Item of a different payment/action class, or model
Ultra Ball alongside Quick Ball. Then optimize payment allocation:
which card pays each search, which target is searched, and whether a
disposable-looking card must instead be preserved for the next turn.
This is a natural point to connect DCI, UDP, connector domination,
and state-dependent AMR to the already-tested physical search kernel.
