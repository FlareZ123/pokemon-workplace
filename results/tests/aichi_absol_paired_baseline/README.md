# First paired Mega Absol vs Regidrago executable evidence

**Agent 23, 12 October 2026.** This finding establishes that the source-verified eighth-place Mega Absol ex/Garbodor 60 can be selected in the same pinned headless Twinleaf runner as the tenth-place Aichi Regidrago VSTAR 60. The result **does not establish matchup strength**.

## Source and settings

[First successful Aichi Mega Absol selectable integration, workflow run 38301959744](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301959744), source research commit a1550920e5768cb8d8ff04ac88af2cc67e1ef830.

The CI job compiled or reused the unchanged upstream Twinleaf pin 3348ebdc898f175a2ed8f999133cd13d1afd01f5, checked complete physical decks (including the two verified same-print Mega Absol label aliases), and ran both orientations at seed 20261012 with native SimpleTacticsAi, uniform research shuffle, separated policy/game randomness, 350 dispatched actions / 25-second wall clock per game and two research hook labels:

- shadow_rider_underworld_door_guard_v1
- regidrago_celestial_roar_any_energy_v1

Sorted 60-copy engine deck SHA-256:
- Mega Absol: 027b603d43f69396195934d66910d4357c8b4cf4ec7c0e883ae6127691840eac
- Regidrago: 2ad6d7d9bf536a16e1f2d237e344c90b919337296482dd4130f4560feaaf7ab0

The uploaded [complete ZIP artifact](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301959744) contained absol-vs-regidrago-paired.json (14,511 uncompressed bytes) with raw game state and telemetry. The artifact was parsed directly to produce the following observations.

## Both native-bot game traces

| Metric | Game 1 | Game 2 |
| --- | --- | --- |
| Seat 1 / Seat 2 | Mega Absol / Regidrago | Regidrago / Mega Absol |
| First turn taken by | Regidrago (seat 2) | Mega Absol (seat 2) |
| Attributed winner | Mega Absol | Mega Absol |
| Engine finished | Yes | Yes |
| End turn | 84 | 63 |
| Dispatched actions | 334 | 282 |
| Elapsed (wall) | 19.038 seconds | 12.917 seconds |
| Prize count remaining (seat 1 / seat 2) | 0 / 6 | 6 / 0 |
| Mega Absol deck's actual attacks | Pound ×1; Static Shock ×14 | Terminal Period ×16; Claw of Darkness ×5 |
| Regidrago deck's actual attacks | **None** | Celestial Roar ×1; Apex Dragon ×2 |
| Mega Absol deck passes | 27 | 11 |
| Regidrago deck passes | **42** | **28** |

**Model sample:** Mega Absol won both completed games, so the fixed two-game sample score is 1.0 for Mega Absol and 0.0 for Regidrago. The actual moving-first deck won one game and lost one; engine seat 1 likewise won one and lost one. This is a successful headless compatibility diagnostic.

**Critical failure of competitive interpretation:** In game one, Mega Absol never attacked with Mega Absol ex; a combination of Pound and Static Shock eventually took six Prizes over 84 turns while the Regidrago bot passed 42 turns and never attacked. In game two, Regidrago did use Apex Dragon twice but passed 28 turns and took zero Prizes. These policies are clearly unable to execute the relevant archetype plan reliably in the observed traces. The apparent 2-0 advantage could be an artifact of that decision policy, not of the underlying paper decks.

The paired-score Hoeffding analysis at only **one paired seed** has radius sqrt(log(40)/2), which exceeds 1.0. Its nominal conditional 95% bounds therefore clip to the entire [0,1] range for either deck even if iid seed assumptions were defensible. No amount of mathematical confidence about a poorly modeled automated player can establish the paper matchup.

## Practical outcome

The complete source-checked Absol 60 has been included in [loadCandidateDecks](../../../simulation/twinleaf/candidate-deck-loader.cjs) and both manual paired workflow selectors. The [loader regression](../../../simulation/twinleaf/test-candidate-deck-loader.cjs) requires all 60 exact engine names, its two specifically audited print aliases, and a physical digest different from Mew/Genesect. The new [bounded one-seed integration CI](../../../.github/workflows/validate-aichi-absol-selectable.yml) passed at the cited research commit and retains raw traces as an artifact.

This increases **selectable archetype** coverage among the [32 published Aichi high finishers](../aichi_2026_top32_proxy/) from 14/32 to **19/32**, subject to keeping the exact print mapping functional in later Twinleaf revisions.

## Next research

Identify why native Regidrago declines to attack, and why the paired model requires as many as 84 turns before a complete outcome. Prioritize competent attacker selection, ability sequencing, energy retrieval, bench management and copied-attack target selection, with a small independently verified action-policy test suite. Include an actual opponent with meaningful counterplay before inferring any competitive relative strength from future match samples. Preserve both raw game outcomes and policy failure metrics.
