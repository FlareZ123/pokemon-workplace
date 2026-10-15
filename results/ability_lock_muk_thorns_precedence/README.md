# Bench Alolan Muk versus Active Iron Thorns ex: asymmetric Ability-lock precedence

## Question and existing prerequisite

Once Alolan Muk enters the Bench through Dream Ball, can Power of Alchemy deactivate Iron Thorns ex Initialization and restore Abilities on Rule Box Evolution attackers? A prior exact typed Dream Ball transaction (results/dream_ball_typed_bench_execution/) proves the direct Stage 1 Bench placement is legal when Dream Ball is taken as a face-down Prize. This result conditions on that entry having occurred.

## Verified card facts

Alolan Muk sm1-58 is a Stage 1 with Power of Alchemy, which removes the Abilities of Basic Pokémon in play, both players' hands and both discard piles. Iron Thorns ex sv6-77, sv6-196 and sv8pt5-32 has Initialization: while Active, Pokémon with Rule Boxes in play on both sides have no Abilities, except Future Pokémon. Iron Thorns is itself a Basic Future Rule Box Pokémon. Source names and exact print texts are checked against the legal bundled card pool.

Shadow Rider Calyrex VMAX swsh6-75 (Underworld Door) and Pidgeot ex sv3-164 (Quick Search) are Evolution Pokémon with Rule Boxes. Genesect V swsh8-185 (Fusion Strike System) is a Basic Rule Box Pokémon.

## Executable conditional results

| Board state | Effective source(s) | Evolution Rule Box Abilities | Basic Genesect V |
| --- | --- | --- | --- |
| Active Thorns, no Muk | Initialization | Suppressed | Suppressed |
| Active Thorns, Bench Muk | Power of Alchemy | Restored | Suppressed |
| Hood on Thorns, Bench Muk | Both sources | Suppressed | Suppressed |
| Same board with Jamming Tower | Power of Alchemy | Restored | Suppressed |
| Hood on opposing Genesect instead | Power of Alchemy | Restored | Opposing Genesect protected |

Power of Alchemy suppresses Thorns' own Initialization because Thorns is Basic. Initialization does not suppress Muk because Muk has no Rule Box. The resulting single directional dependency is Power of Alchemy -> Initialization, so no unresolved reciprocal cycle or invented timing priority is needed.

Stealthy Hood on opposing Iron Thorns protects its holder from Muk's opponent-sourced Ability. Jamming Tower blanks the Hood and restores the Muk -> Thorns edge. A Hood on the opposing Genesect instead protects that Genesect from Muk. The Muk owner still loses their own Basic support Abilities.

## Reproduce and limits

From repository root, run the Python regression in results/ability_lock_muk_thorns_precedence/reproduce.py. A dedicated Actions workflow checks it; changes to shared source geometry also trigger existing profile tests.

The regression models in-play source and target suppression on conditionally constructed boards. It does not execute the prior Dream Ball transaction in the same object representation or model the extra hand/discard effect of Power of Alchemy; the latter is established by card text and catalogued in results/alolan_muk_basic_ability_surface/. It does not simulate attacks, Prize frequency, matchup policies or win rates. The tactical counter can restore Underworld Door in one board state while disabling other draw engines or being answered by a Tool, so its competitive value remains unknown.
