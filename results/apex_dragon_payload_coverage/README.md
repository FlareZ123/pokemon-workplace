# Apex Dragon: semantic completeness of discard-pile Dragon attack sources

## Question

Which attacks printed on effectively legal Expanded Dragon Pokémon are
candidate Apex Dragon bodies, and how much of that source catalog does the
existing conservative execution compiler understand?

This is an attack-source coverage audit rather than a recommendation to use
every Dragon Pokémon in Regidrago. Inclusion in the available source pool
does not imply that a copy is reachable, desirable, discardable, or
affordable in a real game.

## Source and method

`tools/apex_dragon_payload_coverage.py` filters the live paper-Expanded
card pool for Pokémon currently printed with the Dragon type. Every printed
attack is analyzed through the existing full-text coverage classifier.
The output preserves physical print identities separately from
lexical attack-body signatures (attack name, printed damage, normalized
attack text).

The copied attack's printed Energy cost is absent from body-signature
deduplication because the Advanced Player's Rulebook C-18 normally lets
a copying attack use its selected body without paying the selected
attack's Energy cost. Apex Dragon itself still needs to be legally
announced, and energy-discard *effects* in a copied body remain relevant.

Results include distribution of recognized semantic families, attack
prints needing unmodeled text, GX-attack prints requiring the global
GX budget, and nested copy text requiring cycle-safe execution.

## Real source witnesses

- Dragapult ex `sv6-130` Phantom Dive has a supported exact six-counter
  effect in addition to its 200 printed damage.
- Dialga-GX `sm5-100` Timeless-GX has recognized extra-turn semantics,
  with an independent once-per-game GX budget requirement.
- Hisuian Goodra VSTAR `swsh11-136` Rolling Iron includes a protection
  effect not covered by the damage-only parser.
- Regidrago VSTAR `swsh12-136` Apex Dragon is itself a Dragon source
  whose attack text requests another copy, a reason the recursive copy
  kernel must guard its own selections.
- Dragapult ex's Jet Headbutt illustrates a plain printed-damage body.

## Interpretation boundaries

The lexical corpus does not establish the current deck's discard contents,
Prize state, real attack legality, copy-source restrictions from other
effects, retreat/promotion, Energy payment, or matchup value.

The label "verified damage-only" means the full attack text can be handed
to the narrow damage-only program with no further text-body effects.
It does not mean an attack can be selected or performed in every
live game state.

## Reproduction

Implementation: `tools/apex_dragon_payload_coverage.py`.
Single-file regression: `results/apex_dragon_payload_coverage/reproduce.py`.
CI: `validate-apex-dragon-payload-coverage.yml`.
