# Snorlax Block: printed escape-resource audit of the Aichi 2026 field

## Result and scope

Snorlax `bw8-101` has Block: while Active, it prevents the opponent's Active Pokémon from retreating. The Advanced Player's Rulebook distinguishes a normal retreat from a switch caused by an Item or other effect. Cards such as Float Stone and Latias ex's Skyliner reduce or remove Retreat Cost, leaving Block's retreat prohibition intact. Other resources can remove the trapped Active through a switching effect, a pickup effect, or the suppression of Block itself.

The [reproducer](reproduce.py) audits **eight complete paper Expanded 60-card lists** from the project and verifies the exact printed card effects against `resources/cards/en/`. Seven are distinct Aichi archetypes and one is the new four-Block Snorlax derivative. The Iron Thorns and Snorlax English lists are adaptations of Japanese tournament sources.

## Structural first-seven-card evidence

The displayed percentage is the exact probability that a **Basic-valid opening seven** contains at least one of the *reviewed non-Basic* switching, pickup, or self-movement resources listed in the fourth column. It is a first-seven card-access statistic. The percentage does not imply that the card can legally escape an active Snorlax at that instant.

| Aichi archetype | Eligible Basics | Reviewed non-Basic resources | Reviewed direct/pickup copies | Nominal access in Basic-valid seven |
| --- | ---: | ---: | --- | ---: |
| Shadow Rider champion | 14 | 2 | 1 Guzma; 1 Acerola | 21.13991% |
| Vileplume runner-up | 14 | 5 | 2 Guzma; 2 Jet Energy; 1 Cassius | 45.76032% |
| Raichu/Electrode fourth | 13 | 3 | 3 Escape Rope | 30.07903% |
| Mew/Genesect fifth | 11 | 3 | 2 Guzma; 1 Escape Rope | 29.78465% |
| Iron Thorns sixth, English adaptation | 4 | 3 | 3 Guzma | 28.54812% |
| Mega Absol/Garbodor eighth | 10 | 1 | 1 Guzma | 10.85268% |
| Regidrago VSTAR tenth | 15 | 3 | 2 Guzma; 1 Prime Catcher | 30.34375% |
| Four-Block Snorlax experimental mirror | 12 | 3 | 1 Guzma; 1 Penny; 1 Scoop Up Cyclone | 29.93547% |

**Conditional Ability routes excluded from those percentages:** Raichu has one Active Klefki that removes Basic Pokémon's Abilities; Regidrago has one Active Wobbuffet that removes non-Psychic Pokémon's Abilities; Mega Absol has two Garbodor whose Garbotoxin requires a Tool. The Snorlax variant has one Articuno-GX with Legendary Ascent, which can switch itself into the Active Spot when played from hand onto the Bench, provided its Ability can operate.

## Action realism and matchup implications

- **Guzma and Prime Catcher** first need an opposing Benched Pokémon to switch in; they then switch the user's own Active Pokémon. A Snorlax player maintaining an empty Bench can deny the first part. The user still needs their own legal Benched replacement, and Guzma uses the Supporter slot.
- **Escape Rope** switches each side independently when they have a Bench, even if the other side has none. It is an Item and can be blocked by Item lock.
- **Jet Energy** can switch its own newly attached Benched Pokémon into the Active Spot, spending an Energy attachment from hand. This is especially relevant to Vileplume control because it can work without playing a switching Item.
- **Pickup effects** require specific conditions. Acerola requires damage on the targeted Pokémon; Penny is restricted to Basic Pokémon; Cassius and Scoop Up Cyclone each have their own card-type and turn restrictions. Removing the Active also requires a sustainable replacement board.
- **Ability suppression** is a separate answer. Garbotoxin needs a Tool, while Klefki and Wobbuffet must be Active. A Snorlax wearing Stealthy Hood introduces further protection interactions requiring state-specific adjudication.
- **Retreat-cost reducers** such as Float Stone and Latias ex cannot independently override Block. Similarly, Path to the Peak affects Rule Box Pokémon Abilities and will not suppress Block on this no-Rule-Box Snorlax.

The fifth-place Mew and fourth-place Raichu lists contain Escape Rope, a qualitatively different answer from Guzma. Regidrago's Prime Catcher shares Guzma's opposing-Bench prerequisite but has a different Trainer action channel. These are specific strategic reasons to evaluate the opponent's Bench, lock configuration and turn sequence instead of treating all escape resources as interchangeable.

## Computation and limits

The reproducible calculation uses inclusion-exclusion with `N=60`, `h=7`, `B` eligible Basic Pokémon, and `E` reviewed non-Basic resource copies. The numerator for `P(valid AND at least one E)` is `C(60,7)-C(60-B,7)-C(60-E,7)+C(60-B-E,7)`. Dividing by `C(60,7)-C(60-B,7)` gives the conditional percentage in the table.

Opening Prize placement, deck searches, Supporter quotas, card draw, Bench state, other attacks, Item and Ability locks, actual target availability and the opponent's decisions are outside the computed probability. This inventory is an evidence-checked **lower scope of card categories** and an upper-access indicator for those categories, with no match-win estimate or demonstrated chance to escape the Block lock.

CI: [validated GitHub Actions 38611877432](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38611877432). Source decks: [complete published and adapted decklists](../../decks/).
