# Literal healing text compiles into executable board transitions

## Question

Can one rulebook healing family be compiled conservatively from the legal
Expanded card snapshot into the existing board state?

Yes. This result recognizes only complete effect bodies with one of two literal
shapes:

- Heal N damage from this Pokémon.
- Heal N damage from 1 of your Pokémon.

Implementation: tools/healing_profile_compiler.py
Regression: results/healing_profile_compiler/reproduce.py

## Semantic boundary

The compiler scans effectively legal cards from sets marked Expanded-legal and
applies the repository's current ban overlay.

Trainer cards are accepted only when their non-reminder rule body consists
solely of the selected-own-Pokémon healing instruction. Attack profiles are
accepted only when the attack text itself consists solely of self-healing.

Cards with additional consequences, conditions, costs, multiple targets, full
healing, or other wording remain outside this semantic island.

## Execution

HealingProfile preserves source kind, action class, source name for attacks,
target geometry, exact heal amount, and original effect text.

apply_healing_profile removes one damage counter per 10 damage healed, capped at
the Pokémon's current damage.

For a Trainer whose only compiled effect is healing, an undamaged target is
rejected because playing the Trainer would not change game state. A self-healing
attack can still reach the effect executor with zero damage and simply leaves
the board unchanged; attack legality and the rest of attack resolution remain
upstream.

## Validation

The regression requires at least one legal Potion profile with the literal
30-damage selected-target instruction, checks profile-key uniqueness and healing
amount granularity, and executes exact 30-damage and over-heal cases on the
board-position state.

The passing CI scan finds 304 profiles across 187 card names:

- 293 self-healing attack profiles;
- 11 selected-own-Pokémon Trainer profiles;
- heal amounts of 10 (60 profiles), 20 (65), 30 (160), 40 (8), 50 (5),
  60 (2), and 200 (4).

The 11 Trainer profiles are all legal Potion printings in this snapshot. These
counts are properties of the bundled English snapshot under the current
conservative parser.

## Strategic use

Healing changes damage thresholds, future Knock Out sets, Prize timing, and the
value of targeting damaged support Pokémon. An executable healing profile can
therefore feed the same board and damage layers used by attack and Knock Out
research instead of being represented as a generic positive card effect.

## Limits

The compiler intentionally omits broader healing wordings such as heal all
damage, healing multiple Pokémon, healing tied to Energy movement, and effects
with an If you do dependency.

The bundled English card pool also has known regional coverage limits. Profile
counts are a reproducible snapshot inventory rather than a claim about every
Japanese-only Expanded printing.
