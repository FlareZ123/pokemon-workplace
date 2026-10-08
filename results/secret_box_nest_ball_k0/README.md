# Secret Box's Item slot can buy a Tool holder, at a payment cost

## Question

Two distinct Tools A and B require two eligible Pokémon holders. An
in-hand-only Box -> Guzma & Hala abstraction ignores this constraint.
The previous holder-aware opening model required two Basics already
visible and lowered modeled acquisition success substantially.

Can using Secret Box's Item search to fetch **Nest Ball** restore some
of those lost lines after accounting for Nest Ball's own use, the
Guzma & Hala discard payment, and hidden Prize availability of Basics?

Implemented by:
- tools/secret_box_nest_ball_bootstrap.py
- tools/secret_box_nest_ball_k0.py
- results/secret_box_nest_ball_bootstrap/reproduce.py
- results/secret_box_nest_ball_k0/reproduce.py

## Cards and source-grounded mechanics

Card text in the bundled English snapshot (Expanded status "Legal"):

- Secret Box sv6-163: discard three other cards; search an Item,
  Pokémon Tool, Supporter and Stadium.
- Guzma & Hala sm12-193: search a Stadium; optionally discard two other
  hand cards to also search a Tool and Special Energy.
- Nest Ball sv1-181: search the deck for a Basic and place it directly
  on the Bench.

Under the advanced player's rules, a Pokémon may have one attached
Tool at a time (B-02) and the player may play multiple Items per turn
(B-01), barring restrictive effects.

The newly acquired Nest Ball must be **played and discarded** to
produce an additional Basic holder. It is then unavailable to pay
Guzma & Hala's cost. Alternatively, if two eligible holders already
exist, Nest Ball can remain in hand as potential discard material.

The solver enumerates both choices with literal current-hand payments
and typed Box/G&H search slots.

## Local exact discard threshold

Canonical starting state: Box in hand, one protected eligible Basic in
play, D disposable cards in hand. The deck has one each of required
Tools A and B, G&H, Special Energy; Item I represents Nest Ball.

| Starting holders | Searchable Basic | Nest Ball | Stadium copies | Minimum initial D |
| ---: | :---: | :---: | ---: | ---: |
| 1 | Yes | Yes | 2 | **4** |
| 1 | Yes | Yes | 1 | **5** |
| 2 | Any | Yes | 2 | **3** |
| 2 | Any | Yes | 1 | **4** |
| 2 | Any | No | 2 | **4** |
| 1 | No | Yes | 2 | Impossible |
| 1 | Yes | No | 2 | Impossible |

When only one Basic holder exists, a Box-fetched Nest Ball repairs it
at a real cost: the Item output cannot simultaneously provide the
second Basic and pay the downstream Supporter. With two searchable
Stadiums, one additional starting disposable card is needed compared
with the two-holder baseline.

This is an explicit instance of **shared output opportunity cost**.

## Integrated hidden Prize and opening policy

Same illustrative 60-card composition as preceding studies:

- Box 1;
- D20;
- Nest Ball I1;
- Tool A2, Tool B1;
- Guzma & Hala G2;
- Stadium S2;
- Special Energy E1;
- protected P30, including exactly 12 eligible Basics.

Condition on Box in the seven-card opener and at least one Basic among
the other six. Include one turn-start natural draw and six hidden Prize
cards. First Box payment is chosen with K0 information; later Box
search and Nest Ball reveal deck contents before later actions.

For hands with two or more eligible Basics, the original exact
in-hand acquisition policy applies. For hands with only one, a
new solver splits unknown protected cards into hidden **Basic** and
other protected copies before allocating six Prize cards.

It integrates six strategic searched types + hidden Basics with exact
multivariate hypergeometric integer weights. Each candidate initial
Box payment remains fixed across worlds compatible with the hand.

| Terminal objective | K0 success | K1 success |
| --- | ---: | ---: |
| A+B+S+E acquired in hand, ignore holders | 34.324041% | 34.397029% |
| Same, require two *visible* eligible Basics | 15.074459% | 15.104371% |
| Same, allow Box-fetched Nest Ball to Bench a Basic | **24.144851%** | **24.175106%** |

**Nest Ball restores 9.070392 percentage points** of modeled joint K0
success relative to relying only on two visible Basics. It still trails
the unrestricted in-hand objective by **10.179189 points**, because
Nest Ball must be available, Basic must be searchable, and the extra
Item consumption constrains payment.

Exact main fractions:
- K0 with Nest Ball = 21288415854103 / 88169587423918.
- K1 = 106575456852083 / 440847937119590.
- Incremental K0 over strict two-visible holders =
  19993318935507 / 220423968559795.
- K1 - K0 = 866088192 / 2862648942335, or **0.030255
  percentage points**.

The K0/K1 information gap in the Nest Ball case is much smaller than
the original unrestricted in-hand gap of 0.072988 pp. The model now
requires additional Board-compatible outputs and physical Prize
survival before a payment-success event contributes.

The exact accepted-open/turn-draw distribution contains **1,241
distinct visible typed states** after preserving eligible Basic count.
Only 42.502721% of accepted starts have one eligible Basic visible
after the turn draw. In those states Nest Ball can be the decisive
additional-holder route, subject to its search and payment constraints.

## Validation

A separately written physical-card enumerator (not the same category
search recursion) samples every labeled two-Prize world in 48 bounded
states. Its literal Nest Ball play consumes one Item and moves a
specific physical Basic from deck to Bench. It independently verifies
the K0 maximum over fixed pre-search payments and K1 average of
per-world best payments.

The same test verifies that whenever two holders already exist,
Nest Ball's extra route cannot improve the acquisition endpoint and
the result equals the prior trusted K0 model.

An earlier independently labeled Box/Nest/G&H oracle checks 192 state
configurations and exact local discard thresholds. Baseline mixture
ordering is regressed against both the strict-holder model and the
unrestricted hand-only model. GitHub Actions runs 37830758792 and
37831037473 passed.

## State representation caveat

The opening enumerator retains all originally dealt visible cards in a
protected/card-category vector even after a Basic has been placed Active
or Benched. A deployed starter remains an inaccessible protected P
token in the vector, **not an actual hand card**. The restricted
payment/search solver never permits those P tokens to be discarded or
played and therefore obtains the same action feasibility as a
separate-zone physical board representation. Any future effect that
depends on the actual number of cards in hand (such as draw-up-to-five)
will require separating the physical hand from already deployed Basics.

## Limits

All eligible Basics are hypothetically compatible with both Tools,
with free attachment slots. The model guarantees availability of
two compatible holders and acquisition of both Tools in hand. It
does not physically attach them, play the obtained Stadium, satisfy
an attack's Energy requirement, or score an actual KO.

Nest Ball's Item effect is modeled as a deterministic successful
search only if one eligible Basic remains in the deck. Additional
Basic-search Items, alternative before-Box ordering, Item lock,
Bench-full states, tool-target restrictions, broader prize rescue,
and opponent decisions are omitted.

The numerical result demonstrates how downstream search can partially
repair a physical board constraint at a resource cost. It is
conditional on an illustrative deck composition and is **not a
tournament win-rate forecast**.
