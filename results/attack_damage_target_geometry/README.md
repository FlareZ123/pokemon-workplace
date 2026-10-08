# Exact target geometry for direct attack-text damage

## Motivation

The Advanced Player's Rulebook B-08 distinguishes printed Active damage from
damage written in an attack's instructions. An attack with a blank printed
damage field can deal damage to multiple opponent Pokémon, while an attack
with printed damage can also target Benched Pokémon through an additional
damage instruction.

The copy-board pipeline previously exposes one named damage event and one
target per attack-body event. This static research inventories a narrow
mechanically explicit family of target shapes that a future multi-target
executor can use.

## Method

`tools/attack_damage_target_geometry.py` parses the live Expanded card pool
through `simple_attack_board_semantics.legal_cards()`. It accepts **only**
full-text damage clauses, optionally followed by the standard Benched-Pokémon
Weakness/Resistance reminder. It conservatively recognizes direct damage to
one or several chosen opposing Pokémon, to one or several Benched Pokémon, and
to all opposing Pokémon or all their Benched Pokémon. Relevant Basic/Evolution
or ex target filters remain explicit.

The resulting `LiteralDamageGeometry` contains the exact attack identity,
printed Active damage, text damage, target scope, target count if fixed, target
filter, and whether the attack combines text damage with printed Active
damage.

This is a **lexical geometry index**. The parser refuses extra condition
clauses and unsupported target phrases. It does not execute damage, choose
targets, resolve type modifiers or grant legality under locks.

## Live corpus results

On the current effectively legal Expanded English snapshot, CI run
[37769867818](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37769867818)
confirmed **471** exact full-text damage-targeting attack prints:

- **224** damage solely specified by the text, without printed Active damage.
- **247** additional damage clauses attached to printed Active damage.
- **55** each-opponent spread rows (52 unfiltered, 3 ex-filtered).
- **57** each-opponent-Bench spread rows (53 unfiltered, 4 Basic-filtered).
- **137** one, two, or three selected opponent Pokémon rows.
- **222** one, two, or three selected opposing Benched Pokémon rows.

The shape counts partition 471 attack-print rows and represent the narrow
exact grammar, not all attacks capable of non-Active damage.

## Reproducible examples

- Octillery `bw10-19` Sharpshooting: 30 damage to one opposing Pokémon,
  no printed Active damage.
- Kyurem `bw11-43` Glaciate: 30 damage to each opposing Pokémon.
- Charizard `bw11-19` Split Bomb: 40 damage to two opposing Pokémon.
- Darkrai-EX `bw5-63` Night Spear: 90 printed Active damage plus 30
  damage to one opposing Benched Pokémon.
- Landorus-EX `bw7-89` Hammerhead: 30 printed Active damage plus
  30 to one opposing Benched Pokémon.
- Stonjourner `me1-81` Stony Kick: 20 printed Active damage plus
  20 to one opposing Benched Pokémon.
- Mewtwo ex `me55-64` Photon Bullets: 50 damage to each opposing ex.
- Tyranitar-GX `sm8-121` Dusty Ruckus: 130 printed Active damage plus
  30 to each opposing Benched Basic Pokémon.

The corpus regression deliberately rejects Dragapult ex's Phantom Dive,
whose additional counters are an **attack effect** rather than damage,
and the conditional Puffy Smashers-GX text.

## Implications

The correct runtime representation will eventually need one body event with
multiple independent target damage results, a target-specific reaction stream,
the actual attacking Pokémon's type for each calculation, and a shared
end-of-attack Knock Out phase. This catalog supplies conservative source
geometry without mutating the concurrent physical reaction adapter.

## Verification

Run `results/attack_damage_target_geometry/reproduce.py` or the
`validate-attack-damage-target-geometry.yml` GitHub Actions workflow.
