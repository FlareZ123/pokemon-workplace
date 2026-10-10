# Weighted continuation-reversal probability for Double Dragon Energy

## Question

The result `results/energy_discard_continuation_frontier/` counted 80 reversal examples among 81 equally weighted *Basic Energy type compositions*. How does that change when actual physical Basic Energy cards have unequal type multiplicities?

## Model

Fix one active Double Dragon Energy attached to Regidrago VSTAR. Draw **three Basic Energy cards uniformly without replacement** from a hypothetical supply with:

- `g` Basic Grass Energy cards;
- `f` Basic Fire Energy cards;
- `o` Basic Energy cards of all other types.

The hypothetical sampled three-card set is attached to Regidrago alongside DDE. Condition on initially having the Energy types required for Apex Dragon, and suppose the attack copies Salamence ex's Dragon Impact, whose effect discards two Energy.

The minimum *physical-card* payment discards DDE alone. A continuation reversal occurs when that payment makes next Apex Dragon unpayable, while a two-Basic-card payment would retain Apex readiness.

## Closed-form exact result

Write `n = g + f + o` and interpret `C(a,3)=0` for `a<3`.

- There are `C(n,3)` equally likely three-card selections.
- Initially Apex-ready selections: `I = C(n,3) - C(o,3)`. DDE supplies two flexible units, so at least one remaining Basic must supply Grass or Fire.
- Selections preserving Apex readiness *after discarding DDE alone*: `M = C(g,2) * f`. The three Basics alone must be exactly Grass/Grass/Fire.
- Continuation reversals: `R = I - M`.
- Conditional reversal probability, when `I > 0`: `P(reversal | initially ready) = R / I`.

For `g=5`, `f=3`, `o=2`, all 120 three-card selections can initially attack. Exactly 30 contain Grass/Grass/Fire, and 90 produce a continuation reversal. The conditional reversal fraction is **3/4**, or **75%**, in this hypothetical uniform sampling model.

## Validation

`tools/energy_discard_continuation_weighted.py` implements the exact count with integer combinations and `fractions.Fraction`. It independently enumerates each physical-card triple and compares the four count fields across **216** input triples `(g,f,o)`, with each count in `0..5`. All checks passed locally.

Run `python -m tools.energy_discard_continuation_weighted` from the repository root.

## Interpretation and limits

This is a conditional probability over a deliberately constructed *attachment* model. It is **not** a probability over real opening hands, completed attack turns, deck search decisions, opposing disruption, or actual metagame decklists. Players choose what to attach, and DDE acquisition itself is not modeled.

The model demonstrates why uniformly counting type configurations is not an empirical gameplay rate. It offers a closed-form sensitivity analysis to supplement the earlier bounded 80-of-81 type-composition theorem.

Sources and rules assumptions are the same as those in `results/energy_discard_continuation_frontier/README.md`.


## Source-backed example deck composition

The official Pokémon 2025 Expanded strategy article [*A Deep Dive Into the 2025 Pokémon TCG Expanded Format*](https://www.pokemon.com/uk/features/a-deep-dive-into-the-2025-pokemon-tcg-expanded-format) publishes a Regidrago VSTAR list containing **four Double Dragon Energy, three Basic Grass Energy and two Basic Fire Energy**, along with **one Salamence ex**. This verifies that the core engine and attack payload of the constructed witness appear together in at least one published Expanded example list.

Holding one of its DDE copies fixed and imagining **three uniformly sampled Basic Energy cards** from that list's five Basic Energy, the ten equally weighted labeled three-card mixtures have:

- six Grass/Grass/Fire configurations: a one-card DDE discard preserves Apex readiness;
- one Grass/Grass/Grass and three Grass/Fire/Fire configurations: discarding DDE breaks readiness, but a two-Basic payment preserves it.

Thus the conditional reversal fraction is **4/10 = 40%** in this deliberately idealized *three-Basic-attachment sampling* model. The program asserts the exact counts separately. This is a bridge to a real published card-count configuration, **not an observed probability of an in-game attachment state**. Drawing, searching, prize availability, turn-by-turn Energy attachment choices and the likelihood of possessing Salamence ex as an attack payload are not modeled.

The official article predates this October 2026 research and illustrates the format in 2025; it is not offered as evidence of the current metagame.
