# Known negative reprint evidence

The reprint resolver preserves explicit negative evidence alongside positive candidates.

The current known-negative set contains **77 historical prints across 22 names**.

## Official and structural energy evidence

Thirty historical Darkness Energy and Metal Energy prints are Special Energy cards with additional effects, while every current legal Expanded card with those names is Basic Energy. They fail functional identity structurally.

The Tournament Handbook gives Rainbow Energy from Team Rocket number 17 as an explicit non-equivalent example because doing 10 damage and placing 1 damage counter are different mechanics. Team Rocket number 80 has the same current-semantic fingerprint, so the evidence applies to both prints.

## Current-format target divergence

Two historical Life Herb printings, `ex5-90` and `ex6-93`, exclude Pokémon-ex as targets. Current legal Life Herb does not. The current Expanded pool contains a directly legal Pokémon-ex witness, so the target-set difference is reachable. The derivation lives in [../reprint_divergence_predicates/](../reprint_divergence_predicates/).

## Historical Trainer name reuse

[../trainer_name_reuse_divergence/](../trainer_name_reuse_divergence/) adds 16 historical prints across eight same-name families with direct distinguishing states:

| Name | Prints | Decisive divergence |
| --- | ---: | --- |
| Master Ball | 5 | top-seven access versus unrestricted Pokémon deck search |
| Pokémon Breeder | 3 | evolution versus draw-and-heal |
| Pokémon Center | 3 | all-own-Pokémon healing versus one Benched target |
| Max Revive | 1 | discard-to-Bench transition versus discard-to-deck-top transition |
| Revive | 1 | revived Basic receives damage counters historically |
| Devolution Spray | 1 | removed Evolution cards go to discard versus hand |
| Power Plant | 1 | Energy exchange versus Ability suppression |
| Magnetic Storm | 1 | restricted Resistance bypass versus global Resistance removal |

These cases use explicit state witnesses rather than text-distance heuristics.

## Mandatory versus optional selection

[../trainer_optionality_divergence/](../trainer_optionality_divergence/) adds six historical prints across PokéNav, Pokégear 3.0, and Dusk Ball. Their historical text requires choosing an eligible card from the inspected window, while current text uses `You may`. Under current rules, an eligible historical choice is mandatory and the current action is optional, creating a direct material-transition difference.

## Additional source-derived negative evidence

A rules-grounded Trainer audit added eight historical prints across Apricorn Maker, Pokémon Fan Club, Super Potion, and TV Reporter. Friend Ball has a current Restored Pokémon target that historical text cannot search. Historical Computer Search differs from the ACE SPEC copy restriction on its legal Expanded target.

The [historical deck-construction audit](../historical_deck_rules/) adds ten Arceus prints. The older cards allow unlimited copies of that print, while every legal Expanded same-name Arceus print has the ordinary four-copy ceiling. A five-copy deck is a direct rule-category witness.

## Current counts

The 77 known-negative prints are:

- Apricorn Maker: 1
- Arceus: 10
- Computer Search: 2
- Darkness Energy: 15
- Devolution Spray: 1
- Dusk Ball: 2
- Friend Ball: 1
- Life Herb: 2
- Magnetic Storm: 1
- Master Ball: 5
- Max Revive: 1
- Metal Energy: 15
- Pokémon Breeder: 3
- Pokémon Center: 3
- Pokémon Fan Club: 2
- PokéNav: 3
- Pokégear 3.0: 1
- Power Plant: 1
- Rainbow Energy: 2
- Super Potion: 2
- TV Reporter: 3
- Revive: 1

In the current resolver partition, this leaves **3,964** same-name historical prints in `semantic_review`. The positive high-confidence candidate set is **219** prints.

## Evidence policy

Every negative family has a rules-level distinction or a concrete reachable state that separates the historical source from a current legal same-name card. Tournament-policy certification is recorded separately when official guidance exists.

Other unresolved wording variants remain in semantic review until a similarly explicit proof or official source resolves them.

## Reproduction

Run:

`python -m results.reprint_negative_evidence.reproduce`

The new name-reuse witnesses can be reproduced separately with:

`python -m results.trainer_name_reuse_divergence.reproduce`

The optionality witnesses can be reproduced with:

`python -m results.trainer_optionality_divergence.reproduce`
