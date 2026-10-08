# Harto Raichu: visible connector sequencing beats the Quick-Ball-first oracle

## Question

The validated Harto branch originally fixed Quick Ball as the first connector, then optimized whether its one-card payment should be Gladion or a conservative disposable.

What happens when the action space includes other connectors already visible in the same hand?

A much stronger legal policy appears.

Implementation: `tools/raichu_visible_connector_sequencing.py`  
Reproducer: `results/raichu_visible_connector_sequencing/reproduce.py`

## Fixed visible payment witness

The baseline observable branch already guarantees all of these are visible before any search:

- Quick Ball;
- at least one Gladion;
- at least one conservative disposable;
- no visible Alolan Raichu.

If Ultra Ball or Computer Search is also visible, play that stronger connector first and pay its two-card discard cost with:

`Quick Ball + one conservative disposable`

This payment depends only on the visible observation. It preserves Gladion.

Ultra Ball can search the deck for a Pokémon. Computer Search can search the deck for any card.

Therefore:

- if Alolan Raichu is in the deck, the connector takes it directly;
- if Alolan Raichu is Prized, the full-deck search establishes K1 while the visible Gladion remains in hand, so Gladion can retrieve Raichu from the Prize cards.

Within the modeled same-turn Raichu-access endpoint, every observation with a visible Ultra Ball or Computer Search therefore has a deterministic success line.

## Exact result

The calculation reuses the exact opening, first draw, Prize integration, and 1,331 observation partition from `raichu_k0_discard_policy/`.

| Quantity | Exact modeled value |
| --- | ---: |
| Visible Ultra Ball or Computer Search observations | **847 / 1,331** |
| Direct-connector-visible branch mass | **32.562616136%** |
| Baseline K0 success inside that subbranch | **52.413492087%** |
| Ultra Ball visible branch mass | **25.320668406%** |
| Computer Search visible branch mass | **9.070343610%** |
| Both direct connectors visible | **1.828395880%** |
| Baseline optimal Quick-Ball-first K0 success | **32.988188975%** |
| Legal direct-connector-first policy | **48.483600879%** |
| Gain over baseline | **+15.495411904 percentage points** |
| Quick-Ball-first hidden-state oracle | **36.909665108%** |
| Legal direct-first policy above that oracle | **+11.573935771 percentage points** |

The earlier Forest Seal Stone result can be combined with this policy. Use Ultra Ball or Computer Search first when either is visible, otherwise use hosted Forest Seal Stone first when available, otherwise retain the exact baseline Quick Ball payment rule.

That combined visible policy covers **957 / 1,331** observations, or **33.961934924%** of branch probability mass, and reaches **48.690299111%** same-turn Alolan Raichu access. This is **+15.702110136 percentage points** over the baseline and **+11.780634003 points** above the old Quick-Ball-first oracle.

## Why a legal policy can beat an oracle

The earlier oracle was an oracle only inside a restricted action family:

1. Quick Ball must be the first connector.
2. The oracle may see hidden Prize truth when choosing Quick Ball's payment.
3. The rest of the modeled continuation then follows.

It was never a global upper bound over all legal first actions.

Ultra Ball and Computer Search change the action family itself. They both acquire information and directly satisfy the deck-resident target world.

So a legal observation-consistent policy can outperform a hidden-state oracle that is constrained to a strategically weaker first action.

This is a concrete connector-domination result.

## Strategic interpretation

Search order can be more valuable than perfect information about a payment choice.

The same visible hand can contain:

- a weaker connector whose payment creates a K0 decision;
- a stronger connector that consumes the weaker connector as discard material;
- direct target access in deck-resident worlds;
- exact Prize inference in Prize-resident worlds;
- a preserved Prize-recovery Supporter.

A planner that optimizes only the payment of a preselected connector can miss this entire line.

The relevant decision object is therefore the full visible action family, including connector opportunity cost and sequencing.

## Validation

The new calculation independently re-enumerates the grouped physical states and requires exact equality with the validated baseline for:

- observable branch probability mass;
- optimal Quick-Ball-first K0 success mass;
- Quick-Ball-first hidden-state-oracle success mass.

Only after those invariants match are alternative visible first actions credited.

## Limits

This remains a narrow local endpoint: putting Alolan Raichu into hand during the same turn.

It does not value the future consequences of discarding Quick Ball or the disposable card, including:

- later Crobat or other Basic access;
- future Ultra Ball or Computer Search payment stock;
- later discard-pile utility;
- Bench and board-development needs;
- lock effects;
- Supporter contention beyond the preserved Gladion window;
- future Forest Seal Stone or Computer Search opportunity cost;
- the rest of the Raichu/Electrode game plan.

Those omitted utilities can make a locally guaranteed line strategically inferior in a full-game policy.

## Next useful work

The immediate methodological next step is a broader observation-consistent action planner.

Instead of evaluating one prescribed connector and then optimizing its payment, enumerate visible candidate first actions, exact payment witnesses, information transitions, and endpoint continuations together.

For Harto specifically, the next deck-level extension should combine this connector sequencing with the newer Dedenne-GX / Squawkabilly ex fallback work so direct target access and draw-engine access compete in one action graph.
