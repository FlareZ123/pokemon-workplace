# Raichu target access: physical source payment and Prized Gladion fallback

## Research question and source

How much does varying the *actual payment policy* for two-cost Item searchers change immediate access to singleton Alolan Raichu in Harto Miki's 13th-place **2024 Champions League Aichi Expanded** Raichu/Electrode deck?

Published 60: <https://limitlesstcg.com/decks/list/11221>. Earlier deck analyses: [zone-aware Raichu access](../raichu_prize_access/) and [joint Ultra/Computer payment gates](../raichu_multi_search_gate/). The relevant list categories are:

| Role | Cards / copies | Count |
| --- | --- | ---: |
| Target | Alolan Raichu | 1 |
| Prize rescuer | Gladion | 2 |
| Pokémon search | Ultra Ball | 3 |
| Universal search ACE SPEC | Computer Search | 1 |
| Overlap: setup Basic and discard-favorable | Giratina | 1 |
| Other setup-eligible Basics | 3 Unown, 2 Voltorb, 2 Crobat V, 2 Dedenne-GX, Pikachu, Ditto Prism Star, Gengar & Mimikyu-GX, Squawkabilly ex, Flutter Mane, Marshadow | 15 |
| Discard-favorable Energy | 4 Reversal, 4 Counter, 3 Unit LPM | 11 |
| All other resources | Retained as protected | 26 |

This role projection totals **60 cards**. Giratina is cross-classified for legality of both starting placement and hand payment. It is possible to prefer other Active choices for matchup reasons, which this model does not price.

## Exact timing and endpoint

Condition on a valid initial seven containing an eligible Basic, promote exactly one Basic to Active using a stated policy, set six uniformly hidden Prizes, and draw one card going second. The remaining hand has seven cards. At most **one** held Item search source and **one** Gladion are allowed for this access endpoint; no other card effects, Supporter contention, lock, Bench needs, or follow-up turns are simulated.

- If Alolan Raichu is already held, success.
- If it is unprized in deck, a physically payable Ultra Ball or Computer Search can take it.
- If it is Prized, an already held Gladion can retrieve it; alternatively a physically payable Computer Search can inspect the deck, infer Raichu is Prized, take an unprized Gladion from deck, and play Gladion that turn.
- Computer Search is selected first whenever payable, followed by Ultra Ball when Computer Search cannot be paid. This **K0-compatible policy** does not require clairvoyant Prize knowledge: Computer Search chooses the output only after its own deck inspection. Payment cards are committed before inspection.

The model protects target and Gladion from discard under all payment policies, and makes five *hypothetical*, nested payment-permission comparisons. The cost is always two **distinct other cards**:

1. `strict`: only held Special Energy and Giratina (if not Active).
2. `ultra_spare`: additionally discard spare Ultra Ball copies when using one Ultra Ball.
3. `non_ace_sources`: additionally allow Ultra Ball as Computer Search payment, but protect singleton Computer Search when playing Ultra Ball.
4. `any_source`: additionally permit spending Computer Search to pay Ultra Ball.
5. `extra_basics`: additionally allow other non-Active Basic Pokémon in hand to be discarded.

None of these policy changes the actual tournament deck. The later tiers are permissive *access ceilings*, not recommendations to burn useful resources.

## Exact results for the published count projection

Percentage of accepted opening states, including physical Prize cards and the going-second first draw:

| Payment policy | Source held and payable | Target access, static Computer | **Target access, adaptive Computer** | Prized-target Computer rescue only |
| --- | ---: | ---: | ---: | ---: |
| strict | 18.395823% | 30.126094% | **30.578700%** | 0.452606% |
| ultra_spare | 20.153978% | 31.522654% | **31.975260%** | 0.452606% |
| non_ace_sources | 21.758531% | 32.792236% | **33.390969%** | 0.598734% |
| any_source | 21.758531% | 32.792236% | **33.390969%** | 0.598734% |
| extra_basics | 36.086944% | 43.978977% | **44.880944%** | 0.901967% |

**Strict-to-non-ACE source payment increases the modeled immediate Raichu-access endpoint by 2.812269 percentage points.** Moving to the unrealistic all-spare-Basics-permitted ceiling adds 14.302244 points relative to strict. The singleton is Prized in 10.052903% of valid-start states; strict adaptive access conditional on it being Prized is 29.209000%.

A strategically revealing equality: permitting Ultra Ball to discard Computer Search increases the *Ultra-only* direct route (28.360702% -> 29.630284%) but adds **zero** adaptive Raichu endpoint value over `non_ace_sources`. In the same states, Computer Search can instead use Ultra Ball as payment and search Raichu when unprized or Gladion when needed. This is a typed connector-domination result for the specific one-search endpoint. It says nothing about other target searches, future turn playability or whether preserving Computer Search is always optimal.

### Active-selection effect

If Giratina is led whenever it appears in the opener, strict adaptive Raichu access falls from **30.578700% to 29.097533%**, a 1.481168-point loss in this narrow model. The permissive `extra_basics` endpoint is identical (44.880944%) for both choices, as the one available Basic selected as Active simply changes which of two equally acceptable payment Basics remains in hand.

## Method and validation

The [exact implementation](../../tools/raichu_target_payment_frontier.py) sums multivariate opening compositions with exact `Fraction` weights, chooses the Active, then sums all possible first natural draws. After the exposed draw, hidden target and Gladion Prize counts are a hypergeometric allocation from the 52-card unseen pool. All unrelated Prize-card identities are marginalized *analytically*, retaining exact finite-deck correlation with the target and the two Gladion copies. Source presence and discard payment use the resulting **physical seven-card hand**.

The [independent reproducer](reproduce.py) enumerates every labeled initial hand, disjoint Prize set, post-Prize natural draw, Active selection, and all five payment policies on three small real-card-role compositions (six Active-policy fixtures). The 8-state event vector agrees as an exact rational on all fixtures. Additional checks verify nested access, adaptive/static event decomposition, Active policy dominance, and replication of the **30.578700%** earlier strict source-and-Prize benchmark.

Run `python results/raichu_target_payment_frontier/reproduce.py` from the repository root; [manual Windows CI workflow](../../.github/workflows/validate-agent2-raichu-target-payment.yml) runs the same reproducible tests.

## Limits and next work

This is one immediate card-in-hand event. It excludes Forest Seal Stone, Quick Ball, Battle Compressor, Dedenne and Crobat draw, Hisuian Heavy Ball, conditional Gladion use for other Prized cards, Pokémon setup/evolution, actual game-winning Electro Rain lines, opponent actions, matchups and retained ACE SPEC opportunity costs. There is no simulated or measured head-to-head win rate. Best follow-up: place the physically paid, typed, Prize-aware item policy in a larger first-turn action state that can also use Quick Ball and Forest Seal Stone without double-spending hand resources; then value future targets, discarded Energy and Supporter contention. Keep K0/K1 action timing explicit.
