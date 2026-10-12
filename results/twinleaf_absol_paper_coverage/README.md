# Fifth Aichi tournament deck: exact-print Twinleaf compatibility

## Source and pin

Published **Yusuke Kobayashi eighth-place Mega Absol ex/Garbodor** 60-card deck, May 10, 2026 CL Aichi: [source manifest](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json). Source list has **37 distinct exact English print IDs**, 60 physical copies. The published card-name counts and functional English print choices have a separate completed legality proof. The pinned Twinleaf gitlink revision is `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

The initial strict audit uses the shared `simulation/twinleaf/tournament-print-audit.cjs` matcher to compare the source card **set, collector number, normalized literal card name, attack names and Ability names** to compiled Twinleaf card instances. This is a narrow coverage test, not a declaration that the engine implements every effect or current paper legality correctly.

## Initial raw coverage, no aliases

[Manual Windows-independent pinned Twinleaf Ubuntu CI run 38278691254](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278691254) succeeded. The fifth Aichi deck audits as **35 of 37 distinct print signatures (57/60 physical copies)**. The exact two review cases:

| Source English print | Count | Pinned Twinleaf candidate | Evidence |
| --- | ---: | --- | --- |
| `sm9-51` **Tapu Koko ◇** | 1 | `Tapu Koko Prism Star TEU` | Exact Team Up 51, Basic Lightning 130HP, Prism Star tag, **Dance of the Ancients** Ability, **Mach Bolt** attack; name renders a symbol in paper source and words in engine |
| `xy4-92` **Battle Compressor Team Flare Gear** | 2 | `Battle Compressor PHF` | Exact Phantom Forces 92, Item Trainer with source effect text independently verified against engine, **Team Flare Gear** suffix omitted by engine |

The second case was already independently verified for two earlier published Aichi decks by `simulation/twinleaf/baseline-deck-loader.cjs::verifyBattleCompressorLabel`. The first is guarded in the new `simulation/twinleaf/absol-print-verified-aliases.cjs`, requiring exact source print ID, set/number, engine candidate fullName, source Basic Prism subtype/rule, engine Prism Star tag, HP, same attack names and same Ability names.

## Strict verified print-name map

The dedicated `simulation/twinleaf/absol-twinleaf-deck.cjs` composes the shared 37-print signature matcher and just those **two same-print label audits**. If any other source print remains unmapped, the entire 60 is **blocked** rather than filled by a same-named alternative print. `simulation/twinleaf/test-absol-headless-sft.cjs` checks the strict 60-count expansion, the two verified aliases, live CardManager card registration, and an actual seeded bounded native Store / SimpleTacticsAi self-play diagnostic.

The assertions are about **print identity and attack/Ability-name signatures**. Even with the complete map, important simulator semantics can differ from the paper card pool. For example, the exact execution of Tapu Koko's discard-to-Lost-Zone after Dance of the Ancients, its Energy choices, and the modern Mega Absol's interactions still need specific behavioral regressions. SimpleTacticsAi is not established as a competitive policy.

## Reproduction and limitation

Source scripts:

- `simulation/twinleaf/test-absol-print-audit.cjs`
- `simulation/twinleaf/absol-print-verified-aliases.cjs`
- `simulation/twinleaf/absol-twinleaf-deck.cjs`
- `simulation/twinleaf/test-absol-headless-sft.cjs`

Existing manual workflow: `.github/workflows/validate-twinleaf-expanded-bot.yml`, checking out the first-level pinned submodule without recursion, installing exact server dependencies, running source/engine print signature checks and preserving the `twinleaf-absol-print-coverage` JSON artifact. It runs full published 60-card loader and a bounded diagnostic, contingent on strict map status.

The future highest-value work is **semantic card-specific regression and headless policy improvements**, followed by paired-seat and opponent-field experiments. Neither raw print coverage nor a bounded self-play trace constitutes a scientifically supported competitive win rate.
