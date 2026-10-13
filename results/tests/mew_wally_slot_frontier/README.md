# Wally and Tapu Lele-GX: two flexible slots in Aichi Mew/Genesect

This study compares **all six ways to allocate the two original Special Red Card slots** among additional Wally and Tapu Lele-GX copies, retaining the original Wally singleton. Its strongest restricted-access candidate is an experimental [2 Wally / 1 Tapu Lele-GX playable 60](../../decks/mew-genesect-wally2-tapu1/). All options are derived from the same [published fifth-place Aichi 2026 Mew/Genesect list](../../decks/mew-genesect/). No variant has demonstrated match win-rate improvement.

## First-turn going-second experiment

Use the existing [physical Prize and first-draw solver](../mew_wally_tapu_variant/reproduce.py) and its **independent labeled-card exhaustive oracle**, which now additionally checks multiple Wally/Lele multiplicities at three small-deck sizes. Model opening 7 plus first natural draw, six random Prize cards, initial Active Mew V, DCE attached from hand, Wally evolved Mew V through a deck-surviving Mew VMAX, and Benched Genesect V as the source of Cross Fusion Strike copying Techno Blast (210 damage before modifiers). Genesect is held, or reached by an accessible Battle VIP Pass/Quick Ball/Ultra Ball. If Wally is absent, Tapu Lele-GX may be held or searched **into hand** by a Ball, played onto Bench to use Wonder Tag, then obtain a deck-surviving Wally. VIP direct-to-Bench cannot trigger Wonder Tag.

The source and all compared hypothetical 60-card populations contain Mew V4, Genesect V4, Mew VMAX3, DCE4, VIP3, Quick4, Ultra4. Only Wally/Lele/Red Card multiplicities change. Ball discard costs are **mechanically payable in these counted hands**, and are not priced strategically. No Genesect/Dedenne/Crobat draws, Trainers' Mail, Secret Box, Forest Seal Stone, opponent response, or next-turn attack are included. This endpoint is a **restricted subset of first-turn lines**, not a game win rate.

| Wally | Tapu Lele-GX | Remaining Special Red Card | Normal access | Persistent Wonder Tag suppression |
|---:|---:|---:|---:|---:|
|1|0|2 (published)|1.444045204289%|1.444045204289%|
|1|1|1 (earlier variant)|7.326281829134%|1.444045204289%|
|2|0|1|2.766576228949%|2.766576228949%|
|1|2|0|8.483774670866%|1.444045204289%|
|**2**|**1**|**0**|**8.762569342969%**|**2.766576228949%**|
|3|0|0|3.975499350086%|3.975499350086%|

These are exact rational calculations printed by [reproduce.py](reproduce.py). With these restricted goals, **2 Wally / 1 Lele beats 1 Wally / 2 Lele under both normal access and fully suppressed Wonder Tag**. It uses one fewer two-Prize non-Fusion Strike Bench occupant as well. The larger two-Wally/one-Lele attack-access probability does not establish overall deck dominance: both variants sacrifice both late-game Special Red Cards, and second Lele could have other tactical or Prize-survival roles omitted here.

A simple hypothetical model lets an externally supplied probability `p` determine whether Wonder Tag is continuously suppressed before this attack, with no partial recovery. **2 Wally / 1 Lele** and **3 Wally / 0 Lele** tie at exactly `4987144017417877/6246593684973178` = **79.837816719454%** suppression probability. Below that, the 2/1 allocation has higher restricted expected access; above it, 3/0 does. **This is not an estimated metagame frequency.** Against active Path to the Peak removable by a naturally held Sky Field/Field Blower/Lost Vacuum, the true frontier is different; see [joint Path access](../mew_wally_path_joint/) and the [conditional lock matrix](../mew_wally_lock_matrix/). Under Supporter lock, all modeled Wally-based routes disappear.


## Conditional Path / Item / Ability-lock extension

[lock_extension.py](lock_extension.py) composes the previous [validated physical Path and lock model](../mew_wally_lock_matrix/) with all six slot allocations. Under the same restricted opener and six-Prize model, the table below compares the two Lele/Wally mixtures against three Wally. Opponent states are **given**, with no estimate of how often they happen. Path can be removed through naturally seen Sky Field, Field Blower or a mechanically payable Lost Vacuum, if Items are unlocked. The named Item lock blocks Balls/VIP, while independent Ability suppression disables Wonder Tag even after Path removal.

| Opponent's already-live state | 2 Wally / 1 Lele | 1 Wally / 2 Lele | 3 Wally / 0 Lele |
|---|---:|---:|---:|
| No lock | **8.762569342969%** | 8.483774670866% | 3.975499350086% |
| Path to the Peak | **4.611126463163%** | 3.611835530928% | 3.975499350086% |
| Item lock | 1.606679962468% | 1.493180752307% | **1.612285672862%** |
| Item lock + Path | 1.193927481675% | 0.721764900478% | **1.612285672862%** |
| Persistent Wonder Tag suppression | 2.766576228949% | 1.444045204289% | **3.975499350086%** |
| Item lock + persistent suppression | 1.117932655318% | 0.581386703842% | **1.612285672862%** |

**2 Wally / 1 Lele remains above 1 Wally / 2 Lele in all eight Path × Item × Ability conditional cases** of this model. Three Wally can be preferable when Items and/or Abilities are heavily locked. The earlier 79.8378% blocker-mixture threshold describes only the no-Path/no-Item two-state experiment. These conditional scenarios do not assert that independent locks necessarily coexist physically; their sources can suppress one another. An established Active Supporter lock shuts off this particular Wally route across all variants.

Independent physical-card Prize/opening oracles for two repeated-copy N=12 populations passed across all 16 Path × Item × Ability × Supporter states. [Manual CI run 38331341671 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331341671). This quantifies conditional action availability, not opponent board establishment or win probability.


## Two card-specific first-turn extensions

The [Iron Thorns 230-HP damage bridge](iron_thorns_bridge.py) reuses the existing [Muscle Band +20 damage / Iron Thorns Initialization source verifier](../mew_wally_iron_thorns_230/). For an unprotected Active Iron Thorns ex with Wonder Tag disabled, natural Muscle Band + Wally + DCE and a Genesect source enable Mew VMAX's copied Techno Blast to deal **exactly 230 damage**. Wally copy counts 1, 2, 3 yield restricted first-turn-going-second OHKO access **0.235122083152%**, **0.454785706377%**, and **0.659690854468%**, respectively. These exclude further Trainer/Ability draws, opponent protection, and actual opponent setup. Two independently labeled repeated-Wally toy populations reproduce the exact calculation.

The [Hisuian Heavy Ball prize rescue bridge](heavy_ball_prize_bridge.py) covers a disjoint branch excluded from the main study: one singleton Tapu Lele-GX is **Prized**, Wally is absent from the visible eight but survives in deck, Hisuian Heavy Ball `swsh10-146` is in hand, and Genesect is otherwise available to Bench. Hisuian Heavy Ball returns the Prized Basic directly to hand, so playing Tapu Lele triggers Wonder Tag. Conditional on singleton Lele being in the six Prizes, the remaining five Prize selections must jointly leave Wally, Mew VMAX and (when required) Genesect in deck. The exact additional access is **0.125979638889 percentage points** for W1L1 and **0.126438025767 points** for W2L1. Adding only this disjoint route produces **7.452261468023%** W1L1 and **8.889007368736%** W2L1 restricted access; other Heavy Ball routes such as rescuing a Prized Genesect are **still omitted**. Three independent labeled Prize/deal oracle fixtures verify the rescue effect and actual card text. Full [CI 38331868821](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331868821) passed.

Neither extension updates true opponent-frequency or match-win estimates. The improved first-turn endpoint remains a partial subset of legal lines and omits post-attack resource costs.

## Joint Hisuian Heavy Ball target competition

The one-target [joint prize-aware policy](heavy_ball_joint_policy.py) resolves the same source deck's naturally held Hisuian Heavy Ball as a **single consumable Item**. If an ordinary held-Wally or Lele-to-Wally line already works, it is counted in baseline access. Otherwise the policy first tests whether rescuing the singleton Prized Tapu Lele-GX can obtain Wally; if not, it tests retrieving a Prized Genesect V while separately accessing Wally. Every initial hand and first draw are counted once, with the **joint Prize composition of Genesect, Mew VMAX, Wally and Lele** enumerated by multivariate hypergeometric combinatorics. It cannot retrieve both Basics with one Heavy Ball.

| Fixed 60-card candidate | Prior restricted first-turn access | Extra Lele Prize rescue | Extra Genesect Prize rescue | Joint union |
|---|---:|---:|---:|---:|
| Wally 1, Lele 1, Red Card 1 | 7.326281829134% | 0.125979638889% | 0.125177876594% | **7.577439344617%** |
| Wally 2, Lele 1, Red Card 0 | 8.762569342969% | 0.126438025767% | 0.138501806794% | **9.027509175530%** |

These three columns are **mutually exclusive by action-policy classification**. The additional Genesect retrieval is an opportunity already present in the existing one-copy Hisuian Heavy Ball. All computations demand a naturally held Heavy Ball, a Prized target Basic, and the other missing resources. The policy remains simplified in the strategic valuation of Ball discard payments, timing and opponent restrictions, and may omit lines involving other search/draw cards.

Three independent physically labeled N=11, 12 and 13 deck/Prize/draw enumerations match the joint analytical classifier, which also reproduces exactly the separate legacy opening and Lele-Prize-rescue probabilities. [Manual CI run 38332311041 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38332311041). The result is still a **strict subset of opening access**, with no claim of competitive match win rates.

## Independent validation and limitations

- Original English card texts are asserted for Wally `xy6-94`, Tapu Lele-GX `sm2-60`, and Battle VIP Pass `swsh8-225`; duplicate Wally is legal under the ordinary four-copy rule.
- The full new candidate is verified by the existing dated paper Expanded `adjudicate_deck` against every print ID, with 60 cards, 12 Basics, one ACE SPEC, and valid set restrictions.
- Three small physically labeled decks (N=12, N=12, N=13) independently enumerate initial hands, Prize sets and first natural draw for repeated Wally/Lele multiplicities. Each category agrees with the exact hypergeometric solver.

The main loss from using both Special Red Card slots is opposing-hand disruption when the opponent has three or fewer Prizes remaining. The Lele Bench space, Rule Box Ability vulnerability, early lock timing, two-Prize exposure, Mew's Techno Blast next-turn attack prohibition, and potential later Wally dead draws all require actual match modeling. This is a rational opening-access **hypothesis**, with any tournament placement attributable only to the unchanged source list.
