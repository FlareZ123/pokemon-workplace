# Regidrago's first Item commitment has zero modeled K0 information penalty

## Question

Agent5's [exact first-turn joint launch study](../regidrago_joint_launch/) identifies the reachable endpoint where Regidrago V is available and Dragapult ex is discarded using the published 2026 Aichi Regidrago deck's Battle VIP Pass, Quick Ball, Mysterious Treasure, and Battle Compressor. Its full-information action planner can see which Regidrago/Dragapult copies are Prized before selecting any action. During a real game, the player must select an initial search Item and its discard payment using K0 information. How much of the apparent launch probability survives this restriction?

## Action and information semantics

The extension `tools/regidrago_joint_launch_k0.py` enumerates the same category-level opening+one-draw states, legal Basic opener condition, six unknown initial Prizes, and designated safe discard policy as the original study.

For every observable eight-card hand, choose **one first search Item** from the cards physically held. Quick Ball and Mysterious Treasure choices also specify whether to discard a held Dragapult ex or a designated safe card, *before* observing which key copies are Prized. The subsequent deck search reveals the deck composition (K1). The first search's target, including a permissible zero-target selection, and subsequent Item transactions may adapt to the actual deck.

The action set includes Battle Compressor, Battle VIP Pass, Quick Ball, and Mysterious Treasure. The same finite Item and payment rules in `tools/regidrago_joint_launch.py` govern the continuation. The solver uses the maximum expected endpoint success over initial actions, conditional on the hand and marginalized over hidden Prizes, rather than selecting a potentially different initial action in each hidden world.

A successful first Item route is required; a hand with no modeled search Item or no payable Item contributes no success even if it holds Regidrago and a discarded attack payload were theoretically available. All limitations of the original restricted launch model continue to apply. In particular, deck-search selection, tool locks, Ability access, Trainer contention, secondary attack goals, board positions, Energy, evolution and adversarial interaction are not simulated.

## Exact 60-card results

The published list has one Dragapult, three VIP Pass, three Quick Ball, three Mysterious Treasure and one Compressor. The exact-print legal candidate exchanges one VIP Pass for a second Dragapult. `D` specifies the number of *other* non-Basic cards declared safe to discard, as in the original model.

| Build and discard policy | First-Item K0 policy | Full-information line-existence ceiling | K0 penalty |
| --- | ---: | ---: | ---: |
| Published, D=0 | 13.257301009% | 13.257301009% | **0.000000000 pp** |
| +Dragapult, −VIP, D=0 | 19.536019594% | 19.536019594% | **0.000000000 pp** |
| Published, D=10 | 21.702578409% | 21.702578409% | **0.000000000 pp** |
| +Dragapult, −VIP, D=10 | 28.257858951% | 28.257858951% | **0.000000000 pp** |

The equalities are exact rational equalities, with decimals printed for readability. The proposed swap's **6.278719 percentage-point D=0 advantage** is retained after enforcing the first committed Item and discard payment. This does *not* show that Prize uncertainty never matters in Regidrago: the restricted objective and action set admit a first choice that can be followed by an adaptive completion wherever a completion exists. More constrained deadlines, competing targets or setup channels can produce regret.

## Independent physical-card validation

`results/regidrago_k0_joint_launch/physical_oracle.py` is a separately implemented breadth-first search over labeled physical card identities. It exhaustively deals two small ten-card decks with two-card legal Basic openers and one Prize. At each hand it computes the optimal initial Item with hidden Prize information, then allows deck inspection and later physical Item use. The tested small builds reproduce the category solver exactly:

| Ten-card oracle | K0 success | Clairvoyant success |
| --- | ---: | ---: |
| Two Regidrago V, one Dragapult, VIP+QB+MT+Compressor | 23/120 | 23/120 |
| Two Regidrago V, two Dragapult, VIP+QB+MT, one safe discard | 2/15 | 2/15 |

The 60-card exact calculation independently agrees with the prior study's `analyze(...)["joint_any"]` at each tested setting, and never exceeds its full-information bound.

**CI:** [manual validation run 38279803613, success](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38279803613). Both full 60-card regressions and the physical-card BFS oracle execute in the same workflow.

## Hand-by-hand proof of the null information gap

A separate [universal-action witness enumerator](universal_witness.py) uses the generic [first-action value-of-information operator](../first_action_information_value/) and tests **every positive-mass hidden Prize class for every observable hand** under D=0. Every winnable hand has at least one first action that succeeds for all Prize configurations in which any action could achieve the objective.

| Exact D=0 hand-class audit | Published | +Dragapult/−VIP |
| --- | ---: | ---: |
| Legal Basic-valid hand classes with at least one modeled Item action | 1,884 | 2,119 |
| Hand classes with the goal attainable in at least one Prize world | 1,209 | 1,543 |
| Universal first action: Battle Compressor | 752 | 870 |
| Universal first action: discard Dragapult using Mysterious Treasure | 57 | 99 |
| Universal first action: discard Dragapult using Quick Ball | 143 | 236 |
| Universal first action: Battle VIP Pass | 257 | 338 |

These are counts of distinct *grouped hand classes*, with each class having very different physical probability; they are not percentages of matches. The action shown is the earliest one in a predetermined tie-break order among universally successful actions. The audit compares the exact rational hand-weighted total with both the K0 and full-information original solver, and all three agree. It passed [manual CI 38280744737](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38280744737). This supplies a stronger structural certificate than numerical equality alone.

## Implications and next actions

The specific original concern, overvaluation caused solely by assuming a different first Item when key cards are Prized, does not distort these four endpoints. The swap remains a candidate for further testing against actual match goals. The next useful extension should add at least one genuinely competing first-Item use, e.g. reserving Mysterious Treasure for a separate Dragon attacker or seeking another Basic, and apply a two-turn continuation objective. First-turn launch alone cannot establish higher match-win probability.
