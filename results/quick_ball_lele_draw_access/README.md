# Quick Ball -> Tapu Lele-GX -> Gladion after later draws

## Question

The existing opening-window model shows that `Quick Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion` loses realism when Quick Ball lacks a disposable card or Tapu Lele-GX is consumed by the mandatory setup Active role.

How does that correction change after one or more random draws before the Supporter window?

Implementation: `tools/quick_ball_lele_draw_access.py`  
Reproducer: `results/quick_ball_lele_draw_access/reproduce.py`

## Model

The baseline keeps the previous package:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 1 Tapu Lele-GX plus 11 other setup-eligible starters;
- 4 modeled critical non-starter singletons;
- 2 Gladion copies;
- 4 Quick Ball copies;
- 12 non-starter cards currently acceptable as Quick Ball discards;
- remaining cards as other non-starters.

The calculation conditions on a valid opening and at least one modeled critical singleton being Prized.

The sequence is literal for the modeled zones:

1. draw an accepted opening hand;
2. assign the starting Active role;
3. set six Prize cards from the remaining deck;
4. expose a configured number of later random cards from the post-Prize deck;
5. ask whether Gladion can be in hand for the current Supporter window.

A Tapu Lele-GX that is the only setup-eligible Basic in the opening is consumed as the starting Active and is not treated as though it remained in hand. A later-drawn Tapu Lele-GX may be manually played from hand to the Bench and can use Wonder Tag if Abilities and a Bench slot are available.

Quick Ball requires a designated disposable card in the strict model. Spare Quick Ball copies are protected by default rather than silently treated as discard fodder.

## Nested access models

Four models use the same deck slots and random states.

- **Strict:** Quick Ball needs a disposable card, an unprized Tapu Lele-GX still in deck, and an unprized Gladion in deck. Wonder Tag needs Abilities and a Bench slot.
- **No discard gate:** same physical chain, but Quick Ball's discard payment is ignored.
- **Clean Quick Ball:** each accessible Quick Ball is treated as a direct deterministic Gladion out. It still respects Item permission but ignores the intermediate Tapu Lele-GX, Ability, Bench, and discard requirements for the Quick Ball route.
- **Ignore setup loss:** strict mechanics except an opening Tapu Lele-GX used as the only starter is incorrectly treated as if it remained in hand. This isolates the setup-role correction.

These are intentionally nested counterfactuals rather than claims that the optimistic abstractions are legal game states.

## Main result

| Later random draws | Strict | No discard gate | Clean Quick Ball | Ignore setup loss |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 48.569324% | 54.040543% | 57.989748% | 51.482660% |
| 1 | 54.990346% | 59.301569% | 63.527286% | 57.791023% |
| 2 | 60.659748% | 63.972306% | 68.417540% | 63.349968% |
| 3 | 65.621597% | 68.111821% | 72.724794% | 68.203566% |
| 5 | 73.680461% | 75.009334% | 79.821720% | 76.052533% |
| 8 | 82.127521% | 82.583377% | 87.419103% | 84.201273% |
| 12 | 88.935930% | 89.023099% | 93.526976% | 90.642768% |

The zero-draw strict and ignore-setup rows reproduce the earlier opening-window values exactly.

## Finding 1: later draws reduce the discard-payability penalty

At zero later draws, ignoring the Quick Ball discard gate overstates conditional access by **5.471218 percentage points**.

After one draw the gap is **4.311223 points**. After five draws it is **1.328873 points**, and after twelve draws it is only **0.087169 points**.

Later exposure can provide a designated disposable card, draw Gladion directly, or draw Tapu Lele-GX directly. Those events reduce the share of states where Quick Ball is uniquely needed but cannot be paid.

This does not make discard cost irrelevant in general. It shows that a discard gate should be evaluated at the actual action window rather than assigned a fixed penalty independent of prior draw history.

## Finding 2: treating a compound connector as a clean out remains optimistic

After one later draw, strict access is **54.990346%** while the clean-Quick-Ball abstraction gives **63.527286%**, an **8.536940-point** overstatement.

The no-discard model reaches **59.301569%**. The remaining **4.225717 points** between no-discard and clean Quick Ball come from collapsing the intermediate Tapu Lele-GX requirement and its physical availability into a direct Quick Ball -> Gladion edge.

At five draws, the discard-payment gap has mostly shrunk, yet clean Quick Ball still overstates the no-discard physical chain by **4.812386 points**. Access realism therefore cannot be reduced to discardability alone.

## Finding 3: setup-role loss is persistent but increasingly overlapped

Ignoring the starting-Active consumption of Tapu Lele-GX adds **2.913336 points** at zero later draws, reproducing the earlier opening-only correction.

The incremental error falls to **2.800677 points** after one draw, **2.372072 points** after five draws, and **1.706837 points** after twelve draws.

The setup event itself has not changed. Its effect on the access outcome shrinks because later direct Gladion draws and other successful routes increasingly cover states that the illegal setup-preservation branch would otherwise rescue.

This is a useful warning for failure-mode accounting: mechanically distinct constraints are not additive when their affected state sets overlap.

## Finding 4: lock state changes the connector class

With one later random draw in the baseline:

| State | Strict conditional access |
| --- | ---: |
| Items and Abilities available, Bench slot open | 54.990346% |
| Item lock | 33.861828% |
| Ability lock | 24.265475% |
| No Bench slot for Tapu Lele-GX | 24.265475% |

Ability lock and a full Bench both collapse the modeled Tapu Lele package to direct Gladion access. The resulting **24.265475%** equals the random-exposure-only probability for two Gladion copies after eight cumulative cards have been seen.

Item lock is less severe in this narrow package because a naturally preserved or later-drawn Tapu Lele-GX can still use Wonder Tag if Abilities and Bench space remain available.

The result makes lock sensitivity a property of the route, rather than a scalar penalty applied to the deck.

## Validation

The reported values are exact. No Monte Carlo sampling is used.

The reproducer independently exhausts a labeled ten-card deck with two critical cards, one Gladion, one Tapu Lele-GX, one Quick Ball, one disposable card, two ordinary starters, two fillers, a three-card opening, two Prize cards, and two later random draws.

It enumerates every accepted opening, every disjoint Prize set, and every disjoint later-draw set. The labeled frequencies match the category model to floating-point precision for all four access modes.

The reproducer also checks the two published zero-draw regressions and verifies that Ability lock and Bench saturation both reduce the one-draw strict model to the same direct-Gladion baseline.

## Interpretation

A connector's realism changes over time because the state around the connector changes.

For this line, later draws can draw Gladion directly, draw Tapu Lele-GX directly, draw Quick Ball, draw a card that makes Quick Ball's payment acceptable, remove Tapu Lele-GX or Gladion from the searchable deck by drawing them, or make earlier setup-role loss irrelevant through route overlap.

The correct object is therefore a state transition with typed prerequisites. A fixed "Quick Ball counts as one Gladion out" coefficient cannot preserve these interactions.

## Limitations

The model still assumes one Tapu Lele-GX copy, one open Bench slot unless the explicit Bench gate is disabled, no Bench expansion or contraction, no search for Quick Ball itself, no draw Supporter or Ability engine, no competing Quick Ball targets, no opportunity cost for Bench debt or the two-Prize Tapu Lele-GX liability, binary disposable/protected DCI classes, no ordinary Prize-taking, and no opponent interaction.

The random draws are literal unbiased exposure and should not be used as a proxy for targeted search.

## Next useful work

The strongest next extension is connector contention: let the same Quick Ball choose between Tapu Lele-GX for Gladion and a second Basic Pokémon required by an early setup deadline. The route-level access engine here can then be embedded inside a finite-horizon policy objective instead of assuming every usable Quick Ball is allocated to Prize rescue.
