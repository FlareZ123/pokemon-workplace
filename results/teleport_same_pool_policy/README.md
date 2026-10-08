# Same-pool adaptive Quick/Ultra policy with connector-as-payment

## Question

In a single Expanded deck containing both Quick Ball and Ultra Ball,
how should a player select the Item that feeds Sky Field into an already-live
Teleport Room?

The earlier [typed connector comparison](../teleport_connector_comparison/)
analyzed hypothetical decks after replacing one connector with another.
This result keeps both connector names in the same finite card pool and
uses one adaptive policy. It also tests **Quick Ball as an Ultra Ball discard
payment** when Ultra Ball's broader search domain is required.

- Exact policy kernel: [`tools/teleport_same_pool_policy.py`](../../tools/teleport_same_pool_policy.py)
- Reproduction: [`reproduce.py`](reproduce.py)
- Passing CI: [run 37773310171](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37773310171)

## Preconditions

As in the preceding experiments, an established Gothitelle has an unused
Teleport Room Ability, Collapsed Stadium fills four Bench spaces, and the
ordinary Stadium-play quota is exhausted. Sky Field must be discarded from
hand to become a Teleport Room replacement. The specified target singleton
must be unprized and either already held or legally searchable.

The illustrative unknown pool contains 46 cards before Prize placement:
four Quick Ball (Q), four Ultra Ball (U), two Sky Field (S), 16 cards
independently acceptable as an extra Ultra Ball discard (D), one designated
target T, and 19 filler. Then six random Prizes are placed and five
additional cards sampled into the observed hand.

The D group excludes Q, U, S, and T. Unlike the previous isolated
connector comparison, Quick Ball can itself become a strategically
acceptable Ultra Ball payment when its Basic-only search cannot satisfy the
immediate target need.

## Adaptive policy as logical access events

For a required **Basic Pokémon**:

```text
Sky in hand AND (
    Quick in hand
    OR (Ultra in hand AND extra D in hand)
)
```

The Basic must either be naturally held or unprized and still in deck.
Using Quick directly consumes just Sky; when Quick is present, using it as
Ultra Ball payment is unnecessary for this exact single-target objective.
The two routes form an overlapping union.

For a required **Evolution Pokémon**:

- If T is in hand, Quick can discard Sky Field directly and choose no Basic
  search target; alternatively Ultra can discard Sky Field plus D.
- If T is in deck, Ultra must do the Pokémon search. It may pay using Sky
  Field plus a separate D card **or a Quick Ball** that could not search the
  Evolution target itself.

The exact searched-target predicate therefore becomes:

```text
Sky AND Ultra AND (extra D OR Quick)
```

Each positive condition is calculated through multivariate
hypergeometric inclusion-exclusion. The union subtracts overlaps once.
The target-in-deck and target-in-hand branches are disjoint.

## K0 results from the same 46-card pool

| Policy and target objective | Exact success |
| --- | ---: |
| Quick route alone, target Basic | 5.804898% |
| Ultra route alone, target Basic | 4.474518% |
| **Adaptive Quick/Ultra, Basic target** | **9.285497%** |
| Quick route alone, Evolution card to hand | 0.479006% |
| **Adaptive Quick/Ultra, Evolution card to hand** | **5.400934%** |

The adaptive policy covers more states than either individual route in this
specified pool. Its raw improvement must **not** be attributed solely to
adding a particular connector card to an actual deck: the policy has eight
combined connector copies, and real construction requires displacing other
cards to make room. These are within-pool coverage comparisons, with
physical card group counts held fixed.

A separately tested limiting case has **zero independently approved D
cards** while retaining Q4, U4, S2, and T1. Ultra-only access through a
Sky plus D payment is zero, yet the adaptive Evolution-target line remains
accessible with exact probability **1.920335%**. Those successful states
use Quick Ball as Ultra Ball's second discarded card while Ultra Ball
retrieves the Evolution.

## Exact physical witness for the unexpected branch

The regression constructs a concrete hand with Ultra Ball, Quick Ball,
Sky Field, and one ordinary Basic, with a designated Stage 1 Evolution
target remaining in the deck.

It executes:

```text
Ultra Ball:
  discard Sky Field and Quick Ball;
  search Stage 1 Pokémon from deck to hand

Gothitelle Teleport Room:
  discard Collapsed Stadium;
  put the discarded Sky Field into play

Bench ordinary Basic in the newly available space
```

The canonical typed allocator rejects Quick Ball searching the Stage 1
target. Ultra Ball's search accepts the target; its two exact discard
payments are made through the canonical Trainer transaction.

The physical mirror confirms the same Sky Field copy crosses hand,
discard and Stadium-in-play zones; the stage-one target is in hand after
search, and the extra Basic may enter the reopened Bench. The Item and
both discard payment classes are conserved, and the normal Stadium-play
quota remains consumed only by its original use.

## Validation and interpretation

The SFT checks the symbolic inclusion-exclusion union against an
independent exhaustive enumeration of every Prize/hand combination in
six small test populations, spanning both target classes and zero,
one, or two alternate payment cards. All exact probabilities agree.
The named physical sequence and conservation assertions also pass CI.

The result unifies **access edges** with **payment edges**. A connector's
strategic role changes with the desired target class and current
discard availability: Quick Ball may be the cheapest available search
action for a Basic, an otherwise unusable search for an Evolution, or
the exact second discard enabling Ultra Ball to fetch that Evolution.
Treating all those states as a single constant intrinsic value would
lose the tactical distinction.

## Limits and future investigations

Gothitelle setup, Prize rescue, opposing restrictions, and the rest of the
turn remain fixed or excluded. The search/access event is not a game win
probability. Only the specific Ultra/Quick/other discard selection choices
are represented. Other hand cards can be paid where legal, and strategic
retention constraints may prohibit sacrificing Quick Ball in some matchups.

Next steps: allow arbitrary card-specific discard permissions and finite
per-turn interactions; quantify how a player should choose which Item to
preserve when both are accessible and the target class may change over
the following turns.
