# Regidrago natural VSTAR+Energy resource intersection after Item loading

## Research question

The [three-channel access analysis](joint_energy.md) already requires first-turn Regidrago V access, discarded Dragapult ex, and a natural Double Dragon+compatible Energy pair by the second turn. A Regidrago VSTAR still needs to be obtained in time to evolve. Add **naturally drawing Regidrago VSTAR** to the same physical Prize/hand/draw distribution, while leaving all other actions unchanged.

This is an explicit **fourth-channel material requirement**, not an approximation by multiplying independent probabilities. A future card drawn on the second turn can be Regidrago VSTAR or the missing Energy card, but cannot be both at once.

## Physical conditions

The published Aichi 10th-place Regidrago list and [the experimental two-Dragapult counterfactual](README.md) each contain three Regidrago VSTAR, four Double Dragon Energy, six Basic Grass/Fire Energy, and 15 opening Basic Pokémon. The first-turn Item planner is the existing finite, one-use Item action search with zero anonymous discardable filler (D=0). It requires a Regidrago V accessible and a Dragapult ex in discard via Battle Compressor, Quick Ball, Mysterious Treasure, or Battle VIP Pass as applicable.

There are seven opener cards, six hidden Prizes, one normal turn-one draw, and one turn-two draw. The extra draw is evaluated as an unthinned post-Prize **pre-Item reference draw**. All modeled Item searches remove non-Energy/non-VSTAR targets, so legal thinning can only raise the conditional chance of finding missing natural material. A naturally held/drawn Regidrago VSTAR is counted; fetching one with Mysterious Treasure, using other draw Abilities, or acceleration with Crispin is outside the model. This convention makes the four-channel event a restricted source subset, not a comprehensive turn-two attack simulation.

## Exact results

| Material event, Basic-valid openings only | Published, 1 Dragapult / 3 VIP | Candidate, 2 Dragapult / 2 VIP |
| --- | ---: | ---: |
| First-turn Regidrago V access plus discarded Dragapult | 13.257301009% | 19.536019594% |
| Natural Energy pair plus Regidrago VSTAR by turn two (marginal) | 10.811013014% | 10.811013014% |
| **Same-deal Item + Energy + VSTAR four-channel conjunction** | **0.857391220%** | **1.260542292%** |
| Naive product of the first two rows | 1.433248538% | 2.112041621% |

The candidate's restricted four-channel gain is **+0.403151072 percentage points**. Exact fractions for the baseline and variant are `118984284855181/13877478807192000` and `951970917996757/75520744044495750` respectively; the exact paired difference is `68199642392807929/16916646665967048000`.

A marginal `10.811013014%` natural resource event does **not** multiply independently with a `13.257301009%` or `19.536019594%` restricted Item route. Access to all four categories is particularly scarce under this no-extra-draw/no-anonymous-discard scenario, and the early natural cards compete strongly for hand space. The actual deck's Abilities and Supporters can increase resource exposure in a genuine match.

## Exact method and independent verification

The [source-window calculator](../../../tools/regidrago_vstar_natural_joint.py) refines the 34-card anonymous Item-planner filler class into Double Dragon, Basic Grass/Fire, Regidrago VSTAR and neutral filler identities. It enumerates the observed eight-card hand and Prized Regidrago/Dragapult categories, then integrates the conditional hypergeometric outcomes of Prize survival and the one remaining natural draw. Its transition logic explicitly prevents that last card from satisfying both a missing VSTAR and a missing Energy requirement.

The [independent physical oracle](vstar_natural_reproduce.py) completely enumerates labeled physical opening cards, first draws, Prize choices, future draws, and physically payable one-use Item actions across four small toy decks. It agrees exactly with the categorical model for the Item marginal, natural VSTAR+Energy material marginal, and four-channel conjunction. The 60-card fractions and independence counterexamples are regression-fixed. [Manual Windows CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294800649).

## Limits and next experiment

The test is resource availability under favorable uncontested board assumptions. It does not know what the actual opponent does. It omits VSTAR tutoring via Mysterious Treasure, Supporter and Ability draws, Energy accelerating effects, Bench/Active requirements, pre-K1 Item selection, Energy removal, evolving and attacking under Item/Ability lock, and Prize-taking. A four-channel source event is **not a win-rate estimate**.

The highest-impact next step is a physically explicit time-indexed Item policy that can reserve Mysterious Treasure to search VSTAR on either of two turns and price the discarded-card cost. This should be compared to the natural-only result without destroying the already validated published baseline.
