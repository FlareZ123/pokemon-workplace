# Adaptive Quick Ball and Nest Ball sequencing for support pickup replay

## Question

What remains of the optimistic hand-to-Bench support-recovery access result
once **Quick Ball's actual other-card discard payment** is enforced, while
both pickup-assisted recovery routes are still available?

This study composes three mechanisms in a bounded finite-state model:

- A support singleton that started Active can be scooped into hand after
  establishing a backup Basic Pokémon.
- A support fetched onto the Bench by Nest Ball can be scooped and replayed
  from hand to activate its hand-entry Ability.
- Quick Ball can search the support or a backup Basic into hand, but must
  discard another hand card before its search.

Implementation: [bench_trigger_paid_replay.py](../../tools/bench_trigger_paid_replay.py).
Reproduction: [reproduce.py](reproduce.py).
Zero-payment comparison:
[bench_trigger_pickup_replay](../bench_trigger_pickup_replay/).

## Mechanically distinct routes

The support A must be *played from hand onto Bench* to count as triggered.

**Hand access:**
`Quick Ball (discard a card) -> A into hand -> play A onto Bench.`

**Deck-to-Bench replay:**
`Nest Ball A onto Bench (no trigger) -> scoop A to hand ->
play A from hand onto Bench (trigger).`

**Opening-Active recovery:**
`A forced opening Active -> Bench other Basic O
(from hand, Nest Ball or paid Quick Ball) -> scoop A to hand
-> promote O -> hand-play A onto Bench (trigger).`

The dynamic program tracks A in unavailable/hand/deck/Active/pretrigger-Bench
states, ordinary O copies in hand/deck/Bench, remaining Quick Balls,
Nest Balls, approved disposable cards, deterministic pickups, coin pickups,
and effective Bench slack.

Every Quick Ball transition consumes one physically distinct other hand
card: expendable stock, another Quick Ball, Nest Ball, a pickup Item, or
a redundant O held in hand. A pickup spent as payment cannot subsequently
recover the support. Nest Ball can likewise be sacrificed to pay Quick
Ball or used as an actual direct-to-Bench transition. The controller
selects actions and payment types to maximize exact completion
probability, adapting its policy to coin outcomes.

## Exact example

The baseline deck has one singleton A, four Quick Balls, four Super Scoop
Ups, six Prizes, seven opening cards, and one additional random card.
We vary the number of other ordinary Basic starters and Nest Ball-like
direct-Bench Items. All remaining cards are inert filler.

Values below condition on an accepted ordinary-Basic opening. The
zero-payment ideal comparator assumes that every hand connector can
search without paying Quick Ball's actual discard cost.

| Other Basics | Nest Balls | Paid, best-order policy | Idealized search access | Payment/model gap |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 15.508648% | 26.700680% | 11.192032 pp |
| 1 | 2 | 20.472145% | 29.212607% | 8.740463 pp |
| 1 | 4 | **24.496351%** | 31.250163% | 6.753812 pp |
| 3 | 0 | 24.598705% | 37.024241% | 12.425535 pp |
| 3 | 2 | 30.042823% | 39.578696% | 9.535873 pp |
| 3 | 4 | **34.410901%** | 41.640468% | 7.229566 pp |
| 5 | 0 | 29.357083% | 40.580717% | 11.223634 pp |
| 5 | 2 | 34.632914% | 43.123144% | 8.490230 pp |
| 5 | 4 | **38.831391%** | 45.167166% | 6.335775 pp |

In the three-other-Basic example, including four Nest Balls increases
the exact paid success from **24.598705% to 34.410901%**. That 9.812196
point increase combines several mechanisms: direct A-to-Bench replay,
O backup search when A starts Active, and the use of surplus Nest Balls
as discard payment for Quick Ball.

It would therefore be incorrect to attribute the entire gain to
Nest Ball's search action. The simulator preserves all three available
roles and their resource conflicts.

The residual 7.229566-point gap from the zero-payment comparator shows
that the ideal model still overstates trigger access after those
pickup-replay possibilities are counted.

## Exact calculation and verification

The implementation enumerates grouped accepted openings, uniform
six-Prize sets, and one later random draw. Given these zone counts,
it solves a finite, acyclic stochastic action-decision process using
exact `Fraction` values.

An independent physical-label oracle exhaustively enumerates **8,925
accepted opening/Prize/draw worlds** for a 10-card toy deck with A,
two other O, two Quick Balls, one Nest Ball, two Super Scoop Ups, one
approved disposable card, and one filler. Each world identifies the
physical starting Active and remaining searchable deck, then tests
the planner against the grouped state weights. Both produce the
same exact probability **`333/595`**.

Ten standalone action-state witnesses test search payments, two-coin
pickup retries, backup-first Active pickup, direct Bench replay,
tradeoffs involving use or sacrifice of Nest Ball and Scoop items,
and failure when Quick Ball payment would consume the only needed
pickup.

Across nine 60-card deck configurations, the paid adaptive model lies
between zero and the matching zero-payment ideal. A zero-backup,
zero-connector setup cannot recover a forced Active A.

## Interpretation and limitations

Search connectors have multiple, conflicting uses. A Nest Ball may
be the route to the needed Basic, a prerequisite for scooping an Active
support, or a card discarded to fund Quick Ball. The best choice is
dependent on currently available cards and what else the turn requires.

These are restricted **access** probabilities. The model does not
execute Wonder Tag, Dark Asset or Dedechange payloads, validate
opponent/Item lock effects, simulate turn-by-turn search discoveries,
track attached cards, price the ACE SPEC deck slot, or cover unusual
setup cards and other recovery effects. Ordinary held backup Basics are
allowed as discard payment when the planner can afford them.

The next valuable extension is a controlled ablation separating the
different roles of Nest Ball and testing when card availability for
discard, backup creation or direct replay is the binding bottleneck.
