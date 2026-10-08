# Connector execution has three coupled resource axes: cards, board, information

## Scope and provenance

This synthesis relates independently developed Expanded TCG connector research
with the new Secret Box -> Guzma & Hala / Nest Ball family. It is a
methodological research map, not a claim that one connector sequence is
universally strongest.

The underlying goal is to optimize *paper Expanded* line execution under
the actual available card pool, not simply count card-name associations.
Every cited exact percentage belongs to a specified conditional model.

### Supporting studies

- [Secret Box two-Tool pipeline](../secret_box_gnh_tool_pipeline/):
  physical output reuse, independent 1,536-state oracle.
- [K0 hidden Prize payment](../secret_box_k0_payment/):
  irreversible payment before the first deck inspection.
- [K0 opening mixture](../secret_box_k0_opening_mix/):
  frequency-weighted Prize information error.
- [K0 copy density](../secret_box_k0_sensitivity/):
  nonlinear payment-information regime.
- [Basic-holder bridge](../secret_box_k0_bench_bootstrap/):
  physical Board resource geometry.
- [Nest Ball bridge](../secret_box_nest_ball_bootstrap/):
  Item output converted to Bench position rather than payment.
- [Nest Ball hidden Prize mixture](../secret_box_nest_ball_k0/):
  split Basic Prize uncertainty and actual Item play.
- [Early Nest Ball information](../secret_box_pre_nest_information/):
  inspection before Box payment as a costly action.
- [Early Nest Ball opening mixture](../secret_box_pre_nest_opening_mix/):
  positive state-local edge disappearing under a specific deck mixture.
- [Aichi composed connector fan-out](../composed_connector_fanout/):
  another agent's concrete Tag Call -> G&H chain.
- [Aichi exact Box payment families](../aichi_secret_box_payment_families/):
  family-valued discard options and singleton protection geometry.

## 1. One output slot can produce multiple terminal resources

An immediate Secret Box Item/Supporter/Tool/Stadium search is a typed
resource transition. If its output is itself a connector, it can
produce additional, independently typed downstream resources.

Two examples should remain distinct:

- **Two Tool target example:** Box searches Tool A directly, plus
  Guzma & Hala in the Supporter slot. After the Supporter is played,
  its optional full search obtains Tool B plus Special Energy. The
  Box's freshly obtained Item and Stadium may themselves pay the
  two-card G&H cost. If the searchable deck contains *two* Stadium
  copies, three initially disposable cards suffice for final
  A+B+Stadium+Special Energy in hand.

- **Aichi first-turn core example:** Box's Item slot can obtain Tag
  Call, which finds G&H and an additional TAG TEAM payment card.
  G&H then obtains Tool/Energy/Stadium, and Artazon supplies a Basic
  needed by the terminal line. A previously established abstract
  resource calculation requires four initially available payment units
  with replenishment, versus five without. That study checks a
  different terminal demand from the two-Tool example.

In both, the **physical output** and its **eventual terminal value**
must be tracked separately. An output category must be consumed
when it is used as a payment, played as an Item, or attached as a Tool.

## 2. The same output may have mutually exclusive uses

A Box-fetched Nest Ball is an important example.

- If the player already has two compatible Tool holders, Nest Ball
  may serve as a discard-payment card for G&H.
- If the player has only one holder, Nest Ball can put a second Basic
  from deck onto the Bench, but playing it removes the Item from hand
  and may leave too few cards to pay the downstream Supporter.

This creates a physically meaningful opportunity cost.

With a single protected Basic already in play, one searchable Nest Ball
and an extra Basic, the exact two-Tool line requires four initial
disposable cards when two Stadiums are searchable; with only one
Stadium, it requires five. If there are two holders already and
two Stadium copies, three disposable cards suffice.

The relevant value of a given hand card is a property of its
**continuation possibilities**, not an immutable scalar property
attached to its name.

## 3. Search chronology creates an information constraint

Searching the deck reveals its remaining contents; an experienced
player can infer which known card names are Prized.

But **Secret Box discards three cards before searching**.

Let h denote the publicly/privately observable player history,
z the unresolved hidden Prize configuration, and p the initial
Box discard choice. Define W(p,z) = 1 when p permits terminal success
after all later actions are optimized with the remaining-deck knowledge
available at that point.

For the finite set of admissible Box payments P(h):

    K0(h) = max_{p in P(h)} E_z[W(p,z)|h]

    K1(h) = E_z[max_{p in P(h)} W(p,z)|h]

    K1(h)-K0(h) >= 0

The K1 quantity is a **clairvoyant upper bound**. It is only an
attainable policy value if a real, legal earlier action makes z
observable before Box's discard commitment.

For binary success, let E_p = { z : W(p,z)=1 }. Then:

    K1(h) = Pr(union_p E_p | h)
    K0(h) = max_p Pr(E_p | h)

Information has no value for the Box payment if one fixed payment
already covers every hidden world in which *any* payment succeeds.

For the specified two-Tool 60-card toy deck:

- one hand gives K1 72.9416% and K0 66.2086%, a 6.733-point difference;
- averaging exact legal-Basic opening classes, one natural draw and
  six hidden Prizes gives K1 34.3970% and K0 34.3240%, a 0.073-point
  difference.

The second statement is conditioned on Box held in the opening seven
and a valid Basic start; it is not a random tournament win rate.

## 4. In-hand reachability and Board reachability differ

The advanced rules permit only one Tool per Pokémon. Therefore two
different required Tools need at least two compatible untooled
holders, in addition to acquiring both Tool cards.

Holding all other parameters fixed in the illustrative 60-card model:

| Terminal condition | K0 success |
| --- | ---: |
| Acquire A+B+S+E in hand | 34.3240% |
| Also have two eligible Basics already visible | 15.0745% |
| Permit Box-fetched Nest Ball to Bench second Basic | 24.1449% |

The Nest Ball branch recovers **9.0704 percentage points** relative to
the strict two-visible-Basic condition while paying the full Item
opportunity cost.

The two-holder geometry remains idealized: every Basic is assumed
Tool-compatible, no Tool is already attached, and Bench room exists.
Neither model checks attack timing, completed attachments or KOs.

## 5. Earlier information is valuable only after its cost

A held Nest Ball may itself be played *before* Box, allowing the
player to inspect the deck and decide Box's three-card discard with
K1 knowledge.

One exact 24-card two-Prize witness has Box-first K0 success
37/60 and Nest Ball-first success 7/10, an **8.3333-point**
improvement. A literal physical-card oracle verifies the prior Item
leaves the hand while the Basic moves from deck to Bench.

In that state, Nest Ball-first removes the information problem because
it moves the deck observation ahead of the irreversible payment.

However, when the otherwise analogous 60-card deck contains only
**one Nest Ball total**, the exact accepted-opening mixture found
**zero** added success from allowing Nest Ball-first in any of 1,241
typed visible states. There is no backup Nest Ball when the sole copy
is already held. The same action changes resource availability.

This demonstrates how a positive single-state sequencing result can
vanish after realistic copy counts and opening frequencies are
integrated.

## 6. Information and discardability interact by regime

The same exact 60-card two-Tool hand-only model has the following
presearch K1-K0 gaps when protected filler is replaced by disposable
cards (all other component counts held fixed):

| Disposable count | Information gap |
| ---: | ---: |
| 5 | 0.008983 pp |
| 10 | 0.031600 pp |
| 15 | 0.055774 pp |
| 20 | 0.072988 pp |
| 25 | 0.078288 pp |
| 30 | 0.070282 pp |
| 35 | 0.051142 pp |

This nonmonotonicity occurs because information value requires
both a potentially feasible payment and multiple payment-success
events that differ across hidden worlds. Higher disposable density
eventually supplies a robust payment independent of Prize knowledge.

Likewise, with one searchable Stadium and the tested Item copies
0..4, the Box payment information gap is exactly zero, despite
nonzero acquisition success. Adding Stadium and Item redundancy
can create alternative hidden-world-specific payment plans and a
positive information premium.

These are exact **model** outcomes, not observations from matches.

## Suggested implementation contract

For each action in a planner, preserve:

1. **Physical identity and zone** of each resource, including whether
   an Item was played, discarded, or still searchable.
2. **Typed output slots**, their per-action multiplicity, and the
   deck-copy limits shared by all connected search paths.
3. **Action windows and timing**, including available Supporter play,
   Item lock, Tool attachment opportunity and once-per-turn events.
4. **Board resource geometry**, such as Bench space, eligible holder
   types, and occupied Tool slots.
5. **Information state**, especially whether Prize composition is
   inferred before or after a compulsory cost.
6. **Terminal objective**, including whether an in-hand card,
   a physically playable card, an attack, a KO or match victory is
   required.
7. **Probability measure**, which connects local values to the
   frequency of the state in an actual 60-card deck and matchup.

An executable line should preserve action chronology:

    inspect observable state
        -> commit required pre-action costs
        -> reveal/search deck
        -> choose outputs and pay subsequent costs
        -> materialize board effects
        -> check terminal objective

The arrows should not imply every search grants a free deck inspection
before payment. Cards with different orderings may genuinely differ.

## Open research and reproducibility

Every cited exact numerical study includes source, tests and usually
a GitHub Actions workflow in its own result directory. The Aichi
connector example uses a less physical payment-token abstraction,
whereas the newer Box/Nest family uses literal typed payment subsets,
search copies and independently enumerated labeled-card oracles.

Highest-value next steps:

- integrate these state effects into a complete Aichi line including
  real Basic identities, Item/Tool legality, evolution, attack
  timing, and the already-created exact Box payment families;
- evaluate **probability-weighted** prior-search value when
  additional Nest Ball copies are introduced, with their 60-card
  slot opportunity cost included;
- test effects under opponent locks and matchup-dependent usefulness
  rather than treating acquisition as victory;
- compare event-family representations against scalar DCI, possibly
  storing protected-resource cuts and conditional payment policies.

The synthesis should be updated if concrete card-text timing,
independent simulation, or adversarial tests change these conclusions.
