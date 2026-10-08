# Nest Ball first: paying for deck information before Secret Box

## Question

Secret Box discards three other cards before its first deck search. A
prior search can reveal the remaining deck and infer Prizes before
that irreversible payment. However, the search itself may consume a
card needed for the line.

When a Nest Ball is already in hand, should it be played **before**
Secret Box to acquire a second Basic holder and inspect the deck, or
held until **after** Secret Box to preserve discard-payment options?

Implementation: tools/secret_box_pre_nest_information.py.
Independent labeled-card test:
results/secret_box_pre_nest_information/reproduce.py.
Underlying first-search Prize model:
results/secret_box_nest_ball_k0/.

## Execution and information policies

Both plans need two compatible Basic holders and A+B+Stadium+Special
Energy acquired by the end of the turn.

### Box-first

A visible hand contains Secret Box and a Nest Ball. Choose Box's
three-card payment *before inspecting the deck*. Then Box may search
one Item, Tool, Supporter and Stadium. Nest Ball may be played
afterward, if still held, to get a second Basic. A Guzma & Hala
Supporter play can search a Stadium, with an optional two-card
discard to also obtain a Tool and Special Energy.

The policy chooses one Box payment that maximizes success over all
hidden Prize worlds compatible with the initial hand. Post-Box
actions optimize with knowledge of the remaining deck.

### Nest Ball first

Commit to using the **already-held Nest Ball** before Box. If at least
one eligible Basic remains searchable, put it directly on the Bench.
The search now reveals the remaining deck and hence its hidden Prize
complement. Pay Box's three-card cost **after** that observation.

The Nest Ball played before Box has left the hand and cannot be used
for either Box's discard cost or Guzma & Hala's later cost. The
presearch route is valid only when a Basic is actually searchable and
enough other cards remain to pay for Box.

The initial choice between these two action orders is made with K0
information. The solver computes each order's exact conditional
success probability and chooses the better order *before* hidden
Prizes are observed.

## Exact positive witness

A small **24-card toy state**, with two hidden Prize cards:

Visible cards:
- Secret Box already held, outside counted hand;
- Nest Ball I=1;
- two immediately disposable cards D=2;
- Tool A=1, Guzma & Hala=1, Stadium S=1;
- one protected eligible Basic already in play.

The remaining **16 unseen cards** contain:
- D=4;
- another Nest Ball I=1;
- Tool A=1, Tool B=1;
- Guzma & Hala=1;
- Stadium S=1;
- Special Energy E=1;
- protected cards P=6, of which two are eligible Basics.

Condition on this exact visible hand. Choose two unseen cards uniformly
as the hidden Prizes; all other unseen cards form the searchable deck.
Neither model allows the first Box payment to look at Prizes. The
Nest-first policy obtains that information by its genuine Basic search
before paying Box.

| Initial order | Exact terminal acquisition success |
| --- | ---: |
| Box first, optimal K0 fixed payment | **37/60 = 61.666667%** |
| Already-held Nest Ball first, then state-informed Box payment | **7/10 = 70.000000%** |
| Gain from the earlier search | **1/12 = 8.333333 percentage points** |
| Clairvoyant upper bound for either action order | 7/10 |

The Nest-first action repairs one of the two missing holder channels
and lets the payment choice adapt to the actual missing/searchable
copies. Its Item cost matters physically; this gain cannot be obtained
by pretending Nest Ball stays in hand after it is played.

The event is an exact conditional state-local access probability,
**not** a sampled game frequency or tournament win-rate change.

## Fodder-density boundary

The same tested 512-state family showed positive Nest-first gains in
**16** states, all having fewer than three disposable cards in hand.
The tested family varied:
- starting disposable count D=1..4;
- 0 or 1 starting copies of Tool A, G&H and Stadium;
- 0 or 1 additional Nest Ball in unknown cards;
- 1 or 2 unknown copies of Tool A, G&H and Stadium;
- a fixed two hidden-Prize count;
- two initially unknown eligible Basics and bounded other filler.

No tested state with D>=3 benefited from moving the Nest Ball before
Box. The same tests show K0 Box-first equals its clairvoyant K1 upper
bound in every such high-disposable state.

Under the present model's *strictly expendable and otherwise inert*
D type, this is also a direct monotonicity argument:

Once three D cards are in hand, choosing those three as the Box
payment weakly dominates sacrificing any card that may contribute
to the endpoint. Holding additional A/G/S/I/G&H resources cannot
decrease reachability because every later discard/search decision is
optional. Thus the Box payment is already optimal in every Prize
world without needing a prior deck inspection. Any Nest-first action
can be reproduced after Box in its known-deck continuation.

The proof relies on the no-hand-size-effect, no-other-card-cost
abstraction. Real effects such as discard-and-draw, matchups or
one-use triggers could break the simple monotonicity assumption.

## Upper bound identity

For a hidden world z, a clairvoyant Box-first player can emulate
any Nest-first success:

1. Select the same Box payment Nest-first would use, with the
   imaginary advantage of knowing the deck;
2. Search Box outputs, preserving the held Nest Ball;
3. Play the held Nest Ball to Bench the same Basic;
4. Continue with Guzma & Hala and the same resource commitments.

Under this model, the clairvoyant Box-first action always weakly
contains Nest-first success in each hidden world. Hence the
per-world action-order upper bound equals the original Box-first K1:

    E_z[max(Box-first-success(z), Nest-first-success(z))]
      = E_z[Box-first-clairvoyant-success(z)]

The 512-state regression asserts this exact identity.

## Validation

The underlying model uses exact integer hypergeometric Prize-world
weights and rational fractions. Its two policies preserve physical
Item consumption and Supporter quota.

An **independent physical-card-labeled oracle** explicitly enumerates
Prize-card identities, Nest Ball's removal from the hand, one Basic
moving from the deck to Bench, every Box discard payment and each
typed Box/G&H search. It reproduces Nest-first probabilities for 36
small cases without relying on the analytic continuation solver.

A further exact **512-case** scan checks action-order improvement and
the K1 upper-bound identity. The first scan restricted D>=3 and found
zero improvements. Expanded D=1..4 finds the 16 positive witnesses.
CI workflow is
.github/workflows/validate-secret-box-pre-nest-information.yml.

## Limits and application

The Toy state has only 24 cards and two Prizes, and is intended to
isolate the causal sequencing principle. It is **not** a 60-card
Expanded deck consistency estimate.

One prior Nest Ball is assumed to be in hand. Both orders require a
searchable compatible Basic and ordinary Item/Supporter permission.
The model remains limited to in-hand A+B+S+E acquisition with two
free compatible Tool holders. It excludes damage, Tool-specific
targets, Stadium-play state, opponent locks, extra draw engines,
additional Item search chains, and earlier independent deck
inspection.

The next useful step is to condition on realistic 60-card accepted
openings where Box and Nest Ball are both held and compute the true
frequency-weighted marginal value of selecting Nest Ball first.
That requires retaining which Item copies and Basic holders remain
searchable before the initial commitment.
