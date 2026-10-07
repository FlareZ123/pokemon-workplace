# Active/Bench movement text compiler and execution geometry

## Question

Can a narrow, auditable card-text compiler connect common switch / forced-switch / gust effects to the repository's conserved `BoardState` position transition without erasing chooser authority or attack-effect target geometry?

Implementation:

- `tools/position_effect_profile_compiler.py`
- `tools/position_effect_execution.py`

Regression:

- `results/position_effect_profile_compiler/reproduce.py`

## Rules basis

The Advanced Player's Rulebook separates three movement wordings:

1. switching your own Active Pokémon with one of your Benched Pokémon;
2. switching out the opponent's Active Pokémon, where the opponent chooses the new Active;
3. switching in one of the opponent's Benched Pokémon, where the effect user chooses the Benched Pokémon.

The distinction between (2) and (3) is mechanically important for attack effects. The rulebook treats forced switch-out as an effect on the opponent's **Active Pokémon**, while targeted gust is an effect on the **selected Benched Pokémon**. An effect-immunity overlay can therefore block different physical objects even though both successful effects end in the same Active/Bench swap.

## Method

The compiler scans the effectively legal English paper-Expanded snapshot using the repository legality baseline. It deliberately accepts only complete Trainer effect bodies and complete attack-text bodies from a small literal wording family. Historical English wordings are mapped to the same semantic kinds. Movement-relevant current text is applied before compilation: the three Black & White Pokémon Catcher records whose bundled text predates the name-wide erratum are normalized to the current coin-flip wording.

For Trainers, generic Item / Supporter reminder rules are ignored and one simple `You can play/use this card only ...` condition may be preserved. Any additional semantic rule causes exclusion. This is why Counter Catcher compiles with its Prize-count condition while Mallow & Lana is excluded: the latter has a second conditional discard/heal body.

The profile preserves source print and name, Trainer versus attack source, action class, attack name / Energy cost / printed damage, movement kind, chooser authority, rulebook target geometry, a simple Trainer play condition, whether movement requires a heads result, and whether the movement clause is optional.

Execution uses `board_object_kernel.switch_active`, so damage, attachments, physical Pokémon identity, and outgoing-Active cleanup remain owned by the existing conserved board transition.

## Results

The current bundled English snapshot yields **318 print-level profiles across 192 card names**:

| Source | Movement kind | Profiles |
| --- | --- | ---: |
| Trainer | self switch | 17 |
| Trainer | opponent-chosen forced switch | 2 |
| Trainer | actor-chosen targeted gust | 29 |
| Attack | self switch | 169 |
| Attack | opponent-chosen forced switch | 71 |
| Attack | actor-chosen targeted gust | 30 |

Representative compiled witnesses include:

- `bw1-104` Switch: actor chooses its own Benched replacement;
- `me1-126` Repel: opponent chooses its replacement;
- `sm4-91` Counter Catcher: actor chooses the opposing Benched target and the Prize-count play condition is retained;
- `me1-9` Bayleef / Push Down: printed 50 damage plus forced switch-out;
- `me3-30` Clefairy / Follow Me: targeted gust with no printed damage;
- all 11 Pokémon Catcher prints: actor-chosen targeted gust gated by a heads coin result, including `bw2-95`, `bw5-111`, and `bw10-83`, whose raw bundled text still shows the pre-errata guaranteed switch;
- `me2-83` Buneary / Run Around: mandatory attack self-switch;
- `sm3-39` Tapu Fini-GX / Aqua Ring: optional attack self-switch;
- `xy6-1` Exeggcute / Loathe: heads-gated attack self-switch.

The executor refuses coin-gated movement unless an explicit heads result is supplied. This prevents stale raw Pokémon Catcher text from becoming an unconditional reachability edge. The regression also demonstrates the immunity geometry directly. For Bayleef's forced switch-out, blocking effects on the old opposing Active prevents the movement while blocking effects on the chosen Benched replacement does not. For Clefairy's targeted gust, the inverse holds: immunity on the selected Benched target blocks movement while immunity on the old Active does not.

## Strategic interpretation

A position graph should not represent both opponent movement families as a generic `opponent Active <-> Bench` edge. At minimum, an executable edge needs the chooser and the object receiving the effect.

This matters beyond rules correctness:

- forced switch-out gives the opponent replacement choice, so it does not guarantee access to a desired target;
- targeted gust gives the acting player target choice, which supports prize mapping and tactical knockout lines;
- attack-effect immunity can invalidate one family while leaving the other legal in the same board state;
- successful movement can clear transient Active effects through the existing physical board transition.

This is a concrete case of access not implying equivalent control: two cards can both change the opponent's Active Pokémon while exposing different reachable state sets.

## Scope and limitations

This is intentionally a conservative semantic island.

It now compiles the exact pure attack `Switch this Pokémon...` family, including its optional `You may` variant and the standard GX reminder suffix. It does not yet compile movement combined with other attack-body instructions, Abilities with activation / trigger scaffolding, multi-step effects that switch both players, or arbitrary card-text sequencing. Coin-gated movement is covered only for the exact literal heads-gate family.

Attack damage is preserved in the profile but is not executed by `position_effect_execution.py`; damage remains a separate attack-resolution concern. Likewise, source-action legality, attack cost payment, Trainer turn budgets, play locks, performing the coin flip itself, and simple Trainer conditions remain upstream.

The compiler currently scans the bundled English snapshot. The repository's newer regional semantic-source layer shows that region-only cards can exist outside that snapshot, so this profile count should not be treated as proof that no additional regional movement effect exists.

## Reproduction

Run `python results/position_effect_profile_compiler/reproduce.py`.

The regression checks the profile counts, historical/current wording normalization, current Pokémon Catcher errata, exact coin gating, mandatory and optional attack pivot families, exclusion of the tournament-banned Dragapult promo, Counter Catcher's retained condition, exclusion of Mallow & Lana, board movement, chooser authority, and the C-04/C-05 immunity-target distinction.
