# Item-lock gating before Poffin's K1 deck inspection

## Question

Can an active Item lock prevent a Buddy-Buddy Poffin search before the searching
player is allowed to inspect their deck, without losing the exact printed-HP
and public two-target search semantics when the Item is legal?

**Yes.** The integrated wrapper performs a source-scoped hand-Item permission
check before delegating to the validated HP-capped direct-Bench hidden-state
bridge.

Implementation: `tools/locked_hp_hidden_direct_bench_bridge.py`  
Single-file regression: `results/locked_hp_hidden_direct_bench_bridge/reproduce.py`  
[Passing CI run 38241112822](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38241112822)

## Execution ordering

The wrapper carries a single immutable physical-state reference and
observer-relative Prize belief collection. It resolves actions in this order:

1. Validate exact printed Poffin action metadata and the attempted origin of
   the Item play: the player's hand.
2. Project already-active, player-targeted lock restrictions into temporary
   permissions and refuse a prohibited Item before deck inspection.
3. Authenticate selected Basic prints against legal print metadata and their
   printed HP at most 70.
4. Resolve exact public selected-print multiset and K1 Prize information.
5. Execute conserved Item lifecycle and direct-to-Bench physical placement.
6. Apply observer-relative public signaling and the post-search shuffle.

The existing two-target Poffin bridge is reused. This wrapper adds no new
physical movement and does not weaken the 70-HP search ceiling.

## Four-card hidden pool witness

A small physical pool contains singleton 60-HP Elgyem L, 80-HP Murkrow H,
and two inert fillers, with one unknown face-down Prize card. Poffin is held
in hand. The actual world has H Prized and L in the deck.

Under no lock, or only Spiritomb's ACE SPEC restriction (which does not
affect ordinary Poffin), searching L produces:

| Observer | Posterior P(next top = H) |
| --- | ---: |
| Searcher after exact deck inspection (K1) | 0 |
| Opponent after seeing L enter the Bench | 1/3 |

The opponent's probability follows directly: conditional on L being
unprized, H has probability 2/3 of being in the searchable deck and
probability 1/2 of being the top card conditional on that. Thus
(2/3)(1/2) = 1/3.

In the physical result, Poffin moves from hand to discard, Elgyem enters
the Bench, and the remaining physical deck contains an exact sampled
filler top. All card-class totals are conserved, and both observer
posterior distributions assign positive probability to the real world.

Under Vileplume's active Item restriction, the same attempted Poffin
is rejected before target-selection policy processing. An intentionally
malformed search selection policy does not cause a policy validation
error first. This is a useful executable guard against granting an
illegal private deck inspection or K1 Prize knowledge.

## Boundary conditions

The restriction set is already activated and correctly scoped to the
attempted player. Its source condition, Ability suppression, lock expiry,
and target selection are resolved by the upstream source-scoped lock
system, not by this wrapper. The regression validates one selected
Pokémon; the reused HP-bounded hidden-state bridge independently
supports two positive selected targets.

This is a rule-level, physical-state and information-model finding,
without claims about frequency of Item lock or game win rates.
