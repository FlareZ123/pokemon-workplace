# All four Secret Box search categories are needed for universal modeled first-turn coverage

## Claim, scope, and relation to the sample

The Aichi Vileplume 2026 ACE SPEC swap planner considers whether a going-second setup can produce **Bunnelby in play + Technical Machine: Evolution and Jet Energy held**. Full-output Secret Box generates 20,785 extra successes against Grand Tree in 500,000 accepted-opening samples. Within those samples, either **Item + Supporter** or **Tool + Supporter** alone preserves every incremental success.

That empirical complete-coverage statement is sharply limited: the [constructive state test](../secret_box_coalition_synergy/constructive_global_witnesses.py) gives three physically valid, fully ordered 60-card starting configurations from the published Aichi list. They all fail with the Grand Tree baseline and succeed with full-output Secret Box. Taken together, they prove that **each of Item, Tool, Supporter, and Stadium outputs is necessary to preserve all possible modeled incremental successes**, even though no proper subset is necessary on the observed 500k states.

This result applies to the *existing compressed first-turn-core planner and named 60-card deck*. It does not claim that all four searches are compulsory to resolve a literal Secret Box under printed rules or that the alternate ACE SPEC has zero value in other game states.

## Exact physically valid fixtures

The reproducer pins all seven opening cards, all six Prize cards, and the first-turn draw. It constructs a **unique-index permutation of all 60 physical cards** and feeds identical card positions into Grand Tree and Secret Box variants.

### 1. Supporter output is necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Guzma; Cassius; Karen; Faba; Lusamine.
- **Six Prize cards:** Tag Call ×4, Pidgeotto, Gloom.
- **First-turn draw:** Plumeria.
- **All winning output masks:** `4,5,6,7,12,13,14,15` (every one includes Supporter).

The Item search for Tag Call is useless because all four copies are Prized. The required Jet Energy is missing from hand. The Supporter output can reach Guzma & Hala directly, then its paid mode obtains TM: Evolution and Jet Energy while its Stadium search obtains Artazon to Bench Bunnelby.

### 2. Tool and Stadium outputs are both necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Jet Energy; Guzma; Cassius; Karen; Faba.
- **Six Prize cards:** Guzma & Hala ×4, Pidgeotto, Gloom.
- **First-turn draw:** Lusamine.
- **All winning output masks:** `10,11,14,15` (every one includes Tool and Stadium).

Jet Energy is held, but TM: Evolution and Bunnelby are missing. All Guzma & Hala copies are Prized, so Tag Call and direct Supporter output cannot supply the missing components. Tool obtains TM: Evolution, and Stadium obtains Artazon, which supplies Bunnelby.

### 3. Item output is necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Bunnelby; TM: Evolution ×2; Guzma; Cassius.
- **Six Prize cards:** Stealthy Hood ×3, Counter Gain, Artazon ×2.
- **First-turn draw:** Karen.
- **All winning output masks:** `1,3,5,7,9,11,13,15` (every one includes Item).

The Prize cards exhaust *every other Tool* and both Artazon, while both TM: Evolution copies are already held. No Tool or Stadium output can add a disposable card. The opening hand contains Bunnelby and at least one protected TM, but no Jet.

An Item search obtains Tag Call, which in turn obtains Guzma & Hala and Bellelba & Brycen-Man. After Secret Box's three-card cost, the extra TAG TEAM and duplicate TM can pay Guzma & Hala's two-card optional discard, unlocking Jet. With Item removed, direct Supporter alone cannot pay its two-card cost without surrendering an essential held piece.

## Proof of universal necessity

Any fixed subset of output categories that preserves **all** complete-Secret-Box-only successes for the modeled deck must succeed in each constructed state.

- Fixture 1 forces Supporter (bit 4).
- Fixture 2 forces Tool (bit 2) and Stadium (bit 8).
- Fixture 3 forces Item (bit 1).

Therefore, its mask must contain `4|2|8|1=15`. Full-output mask 15 succeeds in each case. Since each fixture has a valid 60-card permutation and passes the exact planner, this is a constructive counterexample to every proper output subset being universally sufficient. The model's full-output function is the reference endpoint, so the all-four mask is trivially sufficient over all possible states by definition.

## Why Monte Carlo missed the Item-only exception

The six Prize cards in fixture 3 comprise exactly the three Stealthy Hood, one Counter Gain and two Artazon cards. Under an unconditioned uniformly shuffled 60-card deck, the chance that this *exact six-card set* occupies the Prize positions is

`1 / C(60,6) = 1/50,063,860`.

Even ignoring the additional opening-hand requirements, 500,000 samples would be expected to show fewer than 0.01 such Prize layouts. This is why the first-turn-core sample can show apparent universal two-category coverage even though an exact reachable state disproves it.

The condition that an opening hand contain a Basic Pokémon introduces a small selection effect; the simple probability above is for an unconditioned shuffled deck, and is used only to illustrate rarity. A stronger enumeration could count entire winning starting-state families, rather than relying on a specific constructed permutation.

## Quantitative rare-Prize analysis

### Exact conditional Prize-event probabilities

The 60-card Aichi list has 14 Basic Pokémon. For `m` specified, physically distinct **non-Basic** cards to be among the six Prizes, with a valid seven-card opening containing at least one Basic, the exact probability is

```text
P(forced Prize event | valid opener)
  = [C(60-m, 6-m) / C(60,6)]
    × [1 - C(60-m-14, 7)/C(60-m,7)]
    / [1 - C(60-14, 7)/C(60,7)].
```

The factor correcting opening validity is necessary: after forcing four Prizes, the two remaining Prize identities are still random. The seven opening cards are uniformly sampled from the 56 cards excluding the forced four, rather than from a particular remaining 54-card deck.

- All four copies of Tag Call Prized: **246321/7805903600**, expected **15.777866** such layouts per 500,000 valid opening trials.
- All four copies of Guzma & Hala Prized: the same probability.
- All three Stealthy Hood, one Counter Gain, and two Artazon Prized: **1195/57598385152**, expected **0.010374** layouts per 500,000 valid trials.

The last event has unconditioned probability `1/C(60,6)`, as described above. Exact rational derivation, an independent exhaustive small-deck oracle, and a replay of the original full 500,000-start seed are in [exact_prize_tail_validation.py](../secret_box_coalition_synergy/exact_prize_tail_validation.py), [rare_tagcall_prize_tail.py](../secret_box_coalition_synergy/rare_tagcall_prize_tail.py) and the reusable [conditional Prize formula](../../tools/accepted_opening_prize_probabilities.py). [All three passed targeted CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38051300162).

In the original 500,000 accepted-opening sequence, **21** openings had all four Tag Call Prized, but only **two** were incremental Secret Box wins where the Item-only route failed. This reconciles the rare Prize event's higher incidence with the two full-audit route exceptions.

### Conditional importance sampling

[Conditional importance sampling](importance_sample_prize_tails.py) constructs a uniformly shuffled physical deck *given* each forced Prize event and a valid opening. For 100,000 accepted starts in each stratum, the reproducible [full CI run passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38051488314):

| Forced Prize event | Incremental full-Box successes | Output requirement within incremental successes | Cases requiring output |
| --- | ---: | --- | ---: |
| Four Tag Call | 7,873 | Supporter | 6,063 |
| Four Guzma & Hala | 3,048 | Tool and Stadium jointly | 1,283 |
| Three Stealthy Hood, Counter Gain, two Artazon | 1,765 | Item | 13 |

For example, to estimate the frequency of a forced-Prize, output-required conjunction among **all valid openings**, multiply the exact forced-Prize event probability by the within-event sampling frequency. The resulting model-based incidence estimates are approximately **1.913224 per million valid openings** for the four-Tag-Call and necessary-Supporter conjunction, **0.404860 per million** for the four-G&H and necessary-Tool+Stadium conjunction, and **0.000002697 per million** for the six-Prize and necessary-Item conjunction. The third is around **one expected occurrence in 370 billion accepted openings** under this model, subject to large conditional sampling uncertainty because only 13 of the 100,000 conditional samples exhibited it.

These are **conditional simulation estimates**, especially uncertain for the last event. They are separate from the exact combinatorial probability of a forced Prize layout, and they do not describe match win rates.

### Constructive Item-payment family and exhaustive test

To prove that the all-six-other-Tools/Artazon Prize exception represents more than one exact fixed opening, [the stratified sampler](stratified_item_payment_tail.py) forces five opening cards: Oddish, the ACE SPEC slot, Bunnelby, and two TM: Evolution. It chooses two other opening cards and the first draw from a specified group of **35 physically distinct generic resource cards**. Its exact event probability among valid openings is

```text
P(six forced Prizes and the entire specified starting-card family)
  = 1/18281877053440.
```

All 5,000 conditional Monte Carlo checks meet the same outcome: Grand Tree baseline fails, full Secret Box succeeds, Item-only succeeds, and full Box without Item fails.

The [exhaustive enumeration](exhaustive_item_payment_family.py) then verifies **19,635** different unordered opening-filler-pairs paired with a distinct first draw, testing two opposing opener-order placements for each, **39,270 full action-planner tests**. All passed. [Stratified and exhaustive CI run 38051738170](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38051738170) is green.

These tests establish a reproducible positive-measure family of Item-indispensable modeled states, even though its mass is so small that ordinary 500k uniform sampling does not discover it. The exact family probability depends on the defined filler set; it is a lower-bound witness family rather than an exhaustive measure of **all** Item-indispensable states.

## Methodological synthesis

The combined evidence gives complementary tools for robust deck research: finite-sample success counts reveal common action paths, targeted exact-Prize conditioning measures rare failure environments efficiently, and physically specified constructive witnesses can disprove apparently universal output substitutions. Discard-material distinctions remain an important realism limitation: searched Stealthy Hood, Artazon, or second TAG TEAM may have later value that the immediate-core solver does not charge.

## Reproduction and limitations

Run `python results/secret_box_coalition_synergy/constructive_global_witnesses.py` from repository root. It verifies card multiplicities, 60 unique physical positions, accepted basic opener, Grand Tree baseline failure, full Secret Box success, and each subset-mask outcome. [Passing CI run 38050810040](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38050810040).

The solver compresses several card identities, does not price future discard utility, and only models a constrained first-turn setup endpoint. These counterexamples are **proofs about that exact computational model**. They identify states a finite random sample can miss, and they motivate exact support-cover verification and more faithful state-level simulator coverage.


## Exact positive-mass lower bounds for every omitted output (2026-10-10)

The [exact portfolio lower-bound reproducer](exact_portfolio_lower_bounds.py) strengthens the three constructive witnesses into **three disjoint families**, rather than relying on one physically ordered deck permutation or only Monte Carlo. [GitHub Actions validation passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38093543413).

Define a conservative 11-card physical discard-filler stock comprising Guzma ×2 and single copies of Cassius, Karen, Plumeria, Gladion, Faba, Lusamine, Peonia, Team Yell's Cheer, and Bellelba & Brycen-Man. These are all non-Basic cards that the compressed first-turn planner treats as generic hand material. Their actual future value is omitted by that solver.

1. **Supporter-indispensable family.** Prize Tag Call ×4, one Pidgeotto, and one Gloom. Open Oddish, the ACE SPEC, plus five of the 11 filler cards, then draw a sixth different filler. Across all **2,772** physically indexed filler/draw configurations, Grand Tree fails, full Secret Box succeeds, and Secret Box with Supporter output suppressed fails. Starting Active is always Oddish, so opening and Prize card order changes no modeled state.
2. **Tool-and-Stadium-indispensable family.** Prize Guzma & Hala ×4, one Pidgeotto, and one Gloom. Open Oddish, the ACE SPEC, one Jet Energy, and four of the 11 fillers; draw a fifth different filler. Across all **2,310** configurations, Grand Tree fails, full Secret Box succeeds, and suppressing **either** Tool or Stadium output causes failure.
3. **Item-indispensable family.** Prize Stealthy Hood ×3, Counter Gain, and Artazon ×2. Open one of **either** Oddish copies, the ACE SPEC, one of **either** Bunnelby copies, both TM: Evolution copies, and two of the 35 generic fillers identified in [the prior exhaustive study](exhaustive_item_payment_family.py); draw a third distinct filler. The earlier 39,270 ordered regression checks establish this generic-stock family's outcome. Swapping physical-copy indices of Oddish and Bunnelby cannot affect the named-card planner's state, giving a **fourfold stronger probability bound** than the previously quoted family restricted to one indexed copy of each.

With a 60-card deck, six Prizes, and a seven-card opener, let **A = 1 − C(46,7)/C(60,7)** be the exact probability of an accepted opening containing an ordinary Basic. The three event-family probabilities conditional on acceptance are:

| Family | Exact probability | Decimal approximation |
| --- | --- | ---: |
| Supporter required | 3/48561235923200 | 6.17776698424e−14 |
| Tool **and** Stadium required | 1/9712247184640 | 1.02962783071e−13 |
| Item required | 1/4570469263360 | 2.18795914025e−13 |

For the Supporter family, the unconditional physical draw probability is

**[2×2/C(60,6)] × [2×C(11,5)/C(54,7)] × [6/47].**

The first factor selects one of two Pidgeotto and one of two Gloom for the remaining two Prizes; the second selects one of two Oddish plus the ACE SPEC and five fillers into the unordered opener; the third selects a sixth filler as the first draw. Divide by **A**. For Tool-and-Stadium, substitute **[2×2×C(11,4)/C(54,7)] × [7/47]** for the opener-plus-draw factors. For Item, the factors are **[1/C(60,6)] × [2×2×C(35,2)/C(54,7)] × [33/47]**, again divided by **A**.

Because the three exact Prize layouts are mutually disjoint, if a proposed fixed subset of Secret Box outputs omits Supporter, Tool, Stadium, or Item, its model loss probability relative to full Secret Box is bounded below by the sum of the applicable **distinct** family probabilities above. Tool and Stadium omissions share one family and are counted **once**. Every proper output subset therefore has a provably positive miss probability in this compressed model.

**Scope:** exact masses are rigorous probabilities for these deliberately narrow events under uniform shuffling and accepted Basic starts. Solver success/failure refers to the existing first-turn-core model, which omits future resource utility, opponent actions, and many tactical constraints. The bounds can be far smaller than the true model-wide output-subset loss. They are mathematical counterexample incidence bounds, not match win-rate claims.


### Enlarged exact families with two flexible Prize cards

The original two fixed Pidgeotto/Gloom Prize identities unnecessarily restricted the Supporter and Tool/Stadium witness families. The [relaxed Prize-pair reproducer](relaxed_prize_pair_lower_bounds.py) instead fixes only four specific cards in the Prizes and allows the other two cards to vary, excluding only pairs that exhaust a necessary two-copy target. [CI run 38093703503 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38093703503).

- **Supporter:** all four Tag Call are Prized. The two remaining Prize cards may be any two of the other 49 physical unselected cards, except the exact two-card pairs exhausting TM: Evolution, Jet Energy, Artazon, or Bunnelby. This leaves **1,172 allowable Prize pairs**. For a five-filler opening, their sum of available first-draw filler choices is **6,744**.
- **Tool and Stadium:** all four Guzma & Hala are Prized, with Jet Energy already held. The two other Prizes may be any two of 49, except pairs exhausting TM: Evolution, Artazon, or Bunnelby. This leaves **1,173 allowable Prize pairs**, with **7,875** eligible filler first-draw choices for the fixed four-filler opening.

The code verifies the exact pair counts against explicit named physical card identities and tests the required baseline, full-output, and output-ablated action-planner outcomes for every allowed Prize pair under a canonical filler opener. The previously verified full filler/draw enumerations cover the alternative filler choices for fixed Prizes. The generalization across both dimensions also follows structurally: all chosen 11-stock fillers compress to the same generic in-hand resource; available unprized required target copies retain the same search path; and no Jirachi is active. In this restricted planner the remaining differences in unused deck cards cannot invalidate the certified path.

Let **A = 1 − C(46,7)/C(60,7)** again. After fixing the visible opening family, the four forced Prizes can be chosen in one way. The weighted two-extra-Prize count for Supporter is

**6×C(49,2) − 6×48 − 4×6 = 6744**;

for Tool and Stadium it is

**7×C(49,2) − 7×48 − 3×7 = 7875**.

The middle subtraction counts draws consumed by an extra-Prized filler. The final subtraction excludes pairs exhausting a target supply.

The corresponding **exact accepted-opening lower bounds** are now:

| Necessary output(s) | Enlarged exact family probability | Improvement over earlier fixed-six-Prize family |
| --- | --- | ---: |
| Supporter | **843/48561235923200 ≈ 1.73595252257e−11** | 281× |
| Tool and Stadium | **225/7769797747712 ≈ 2.89582827386e−11** | 281.25× |
| Item | **1/4570469263360 ≈ 2.18795914025e−13** | Unchanged |

For any proper enabled-output mask **M**, a guaranteed miss probability relative to the full-output solver is at least

**P(S missing) × 843/48561235923200 + P(Tool or Stadium missing) × 225/7769797747712 + P(Item missing) × 1/4570469263360**,

where each P in this displayed expression denotes a zero-or-one indicator for whether the relevant category is omitted by that fixed mask. The disjoint forced Prize sets permit addition. For the same mask, the actual miss probability can be much greater. The bounds quantify model-specific failure support; they do not estimate tournament rates.


### Exhaustive compressed cross-product certificate

The [grouped cross-product verification](grouped_cross_product_certificate.py) removes the earlier methodological gap between testing every Prize pair for a single filler arrangement and testing every filler arrangement for a single Prize layout. [GitHub Actions run 38093867316 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38093867316).

It partitions physically distinct unused cards into the source planner's **11 named deck-compression classes** plus one class of ignored card identities. The 11-card discard-filler stock contains ten cards in the other-Supporter class and one Bellelba in the other-TAG-TEAM class. Every legal combination of opener filler allocation, extra Prize class pair, and eligible first-draw filler class is weighted by the exact number of underlying physical copies. The test calls the **unmodified first-turn planner** for every resulting compressed state and verifies the Grand Tree baseline fails, full Secret Box succeeds, and the relevant category-ablation mask fails.

The weighted count agrees exactly with the physical formulas above for each family. It therefore certifies the **complete cross-product** of the specified Supporter and Tool/Stadium families, without a sampling assumption. It also explicitly verifies each unused-card class, including Basic cards, is legitimately pooled only when it cannot enter the initial Active or first-draw filler selection. Starting Active remains Oddish throughout, so Jirachi top-five effects never arise.

The category model remains restricted to the original immediate-core solver, which compresses downstream value and omits realistic opponent actions. The conclusion about exact family probability is stronger than a simulation estimate, while the conclusion about in-game strategic value still inherits the simulator's limited objective.
