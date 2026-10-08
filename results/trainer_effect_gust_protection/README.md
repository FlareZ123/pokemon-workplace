# Item and Supporter gust effects have different protected target sets

## Research question

Can two physically available gust cards still have different **effect-legal Bench targets** because defensive Abilities or Tools react to the Trainer type played from hand?

Yes. The bundled Advanced Player's Rulebook distinguishes an effect that chooses an opposing Benched Pokémon and switches it Active (C-05), from an effect that merely changes a player's own Active (C-03). The rulebook's E-29 also describes preventing card effects from Trainer plays. The reactive-card catalog identified print-specific protections.

## Conservative mechanical compiler

`tools/trainer_effect_gust_protection.py` represents **six manually audited Pokémon Ability prints** and **one Pokémon Tool print**. Each profile records the protected card classes, whose Pokémon are protected, and which source conditions must hold.

It checks actual object IDs on a `BoardState`, including provider Active position, target Bench position, Pokémon tags, `abilities_enabled`, Tool identity and `tool_effect_enabled`. It only evaluates the **target immunity to an already identified Trainer effect**. The caller independently determines whether an Item or Supporter can be played from hand, has been successful, and meets all other card-specific conditions.

### A small source-dependent target matrix

| Defender configuration | Item gust: Prime Catcher | Supporter gust: Guzma / Boss's Orders |
| --- | --- | --- |
| Togekiss `bw8-104` with Bright Veil Active, ordinary Bench target | Target protected | Target not protected by Bright Veil |
| Diancie `swsh10-68` Active, Basic Bench target | Target not protected by Princess's Curtain | Target protected |
| Axew `sm11-154` Unnerve, targeting that Axew | Protected | Protected |
| Articuno `sm9-32` Active, Water Bench target | No protection by Blizzard Veil | Protected |
| Cetitan ex `sv10-65` Snow Camouflage, targeting that Cetitan | Protected | Protected |
| Rhyperior `sv7-76` Wide Wall Active | No protection by Wide Wall | Protected |
| VMAX/VSTAR with enabled Leafy Camo Poncho `swsh12-160` | No protection by Poncho | Protected |

`Protected` means the specific card effect cannot execute against that target under the represented prevention text. The outcome of attempting to play a card whose target is protected is a separate question; in particular, legal-play state-change requirements and other conditional parts of a Trainer are **outside this predicate**.

## A physical feasibility counterexample

With an opponent's Togekiss Active and another target on its Bench, both Prime Catcher and Guzma can be physically represented by the repository's paired-switch kernel. Their source cards are different action classes.

The target-effect predicate blocks the **Prime Catcher Item** effect from moving the chosen protected Bench Pokémon, while permitting the **Guzma Supporter** effect to choose it. The direction reverses with Diancie Active and a Benched Basic: Prime can target it, Guzma cannot.

The opponent's Pokémon count, position, and Prize values can be unchanged. Which source card is available determines whether the tactical Bench target can actually be reached.

## Important conditions

- When Togekiss, Articuno, Diancie or Rhyperior moves off Active, its Active-dependent protection ceases.
- A Pokémon Ability that is suppressed by an applicable Ability lock does not provide this protection. The board must supply the effective `abilities_enabled` state, which can come from the causal lock owner.
- A disabled Leafy Camo Poncho has no protective effect. The board's Tool state must be current.
- Copied Supporter text executed by an **attack** is outside a `Trainer played from hand` protection trigger, even if the copied effect's words resemble a Supporter.
- Other immunity, attack damage effects and the full set of conditional Trainer restrictions remain separate.

## Reproducibility

`python results/trainer_effect_gust_protection/reproduce.py`

The regression validates the profile names and Ability/effect text against the bundled prints, verifies the source-type matrix, position and Ability suppression counterfactuals, Tool disablement, Bench-only targeting, attack-origin exclusion and physical paired-switch feasibility.

This is a **bounded and human-audited protection compiler**, not a universal parser for every E-29 phrase in the card pool. See the [reactivity census](../trainer_play_reactivity_catalog/) for unimplemented candidates.
