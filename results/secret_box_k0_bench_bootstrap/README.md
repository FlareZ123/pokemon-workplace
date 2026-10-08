# From Tool acquisition to physically attachable board capacity

## Question

Earlier exact Secret Box -> Guzma & Hala models score acquisition of
two distinct Tool cards A+B plus a Stadium S and Special Energy E.
Those cards can all enter the hand while there are too few Pokémon in play
to attach both Tools.

What happens if we require two separate eligible Pokémon holders to be
available from the visible opening plus one natural draw?

Implementation: tools/secret_box_k0_bench_bootstrap.py.
Independent physical Basic-count check:
results/secret_box_k0_bench_bootstrap/reproduce.py.

## Model and rule boundary

The Advanced Player's Rulebook B-02 permits any number of Tools to be
played per turn but allows **only one Pokémon Tool attached per Pokémon**
at a time. It follows that two distinct Tools require at least two free
compatible Pokémon holders in play.

The abstract deck has 60 cards: Box 1, D20, I1, Tool A2, Tool B1,
Guzma & Hala2, Stadium2, Special Energy1, protected P30; 12 of the 30
protected cards are eligible Basic Pokémon. Box is conditioned present
in the seven-card opening hand and an eligible Basic must be among the
other six. One natural draw occurs on the modeled player's turn.

All twelve Basics are assumed to be mutually compatible with both Tools.
Every Basic visible after the draw can be legally placed into the Active
Spot/Bench, with no prior Tools attached, no lock, and enough Bench space
for the modeled two or three holders.

This terminal event therefore requires:
1. Secret Box-first acquisition of A+B+S+E in hand after all payments;
2. at least k distinct visible Basics, where k=2 for the primary result.

The Tool attachments themselves are not simulated. Under the ideal
assumptions, basic-count sufficiency ensures that attaching A and B
to distinct holders would be geometrically possible. Other downstream
requirements remain unchecked.

## Exact joint results

All percentages condition only on Box in the original seven and at
least one Basic in the original other six; requiring a second or third
Basic is part of the measured event, not an additional conditioning
restriction.

| Requirement | Holder availability | K0 joint acquisition | K1 joint acquisition | Information penalty |
| --- | ---: | ---: | ---: | ---: |
| >=1 eligible Basic | 100.000000% | 34.324041% | 34.397029% | 0.072988 pp |
| >=2 eligible Basics | 57.497279% | **15.074459%** | 15.104371% | 0.029912 pp |
| >=3 eligible Basics | 18.536452% | **2.809381%** | 2.813242% | 0.003861 pp |

Exact two-holder fractions:
- P(holders>=2) = 4527487/7874263.
- K0 joint = 123293954359/817899697810.
- K1 joint = 66520787941/440407529590.
- K1-K0 = 171256272/572529788467.

Three-holder K0 = 16084545385/572529788467; gap =
22108020/572529788467.

Requiring **two visible Basic holders** reduces joint terminal success
from 34.324041% to 15.074459%, a **19.249581-point decrease** for this
abstract composition. The conditional success given sufficient holders
is also lower than the unconstrained figure; the availability of two
Basics occupies hand slots that might otherwise contain expendable
payment stock and essential target cards.

The last causal statement is a model-consistent explanation, **not** an
isolated experimental causal estimate of each competing card category.

## Exact combinatorial validation

The calculation retains separate Basic versus other protected copy
counts while enumerating every accepted six-card opening and turn draw.
It collapses them into P only when passing a visible hand to the original
K0 hidden-Prize payment solver. Basic holders remain protected from
discard.

An independently written labeled-card oracle on a 14-card toy deck
enumerates each accepted Basic-containing initial hand and each legal
turn draw. It exactly reproduces the category solver's **163 distinct
(Basic count, typed visible hand) states and 3,465 weighted sequences**.

The reference one-holder model reproduces the previously validated
K0/K1 opening mixture exactly. The sufficient-holder probabilities
also reproduce a separate binomial count by category:
  
    P(Basics visible >= k | Basic in first six, Box held)
      = sum_{s=1..6} C(12,s)*C(47,6-s)*
        [ (12-s)*1{s+1>=k} + (47-6+s)*1{s>=k} ]
        / ( [C(59,6)-C(47,6)] * 53 )

All compared probabilities are exact rational values. The two-holder
K0/K1 difference cannot exceed the one-holder difference, as tested.

GitHub Actions runs 37830425907 and the subsequent workflow dispatch
validate the implementation. An initial workflow run failed due to an
incorrect *test expectation* (170 states instead of the independently
measured 163) and was fixed; no solver regression was needed.

## Interpretation and limits

This illustrates why in-hand search reachability can overstate useful
board access. A full Expanded planner must reserve compatible physical
holders, account for existing attached Tools, permit legal Basic search
and Bench placement, and enforce Item/Tool locks and any Tool-specific
holder restrictions.

The Basic-count event is deliberately conservative: a player could use
the searched Item or other effects to acquire more Basics after the draw.
Such options are not present in this bounded model. Conversely, some
real Tools require specific Pokémon targets; our ideal all-compatible
holders assumption overstates those cases.

The reported gap is an **illustrative objective-specific access loss**.
It is not evidence of tournament win-rate change.
