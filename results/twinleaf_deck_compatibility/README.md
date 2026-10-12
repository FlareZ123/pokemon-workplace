# 2026 Aichi paper Expanded decks: exact-print Twinleaf implementation audit

**Date:** October 12, 2026. **Engine:** pinned `twinleafgg/twinleafgg` Gitlink `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. **Evidence:** [green manual CI run 38246939386](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38246939386), including compiled engine checks, all four print/signature audits, full-deck materialization, paired real first-turn setup, Underworld Door regression, and cleaned-up bot setup. The `twinleaf-print-coverage` artifact with all per-print diagnostics was uploaded. Earlier [run 38244989239](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38244989239) completed the audit but was cancelled after a bot process retained live timers; the CLI cleanup issue was subsequently fixed.

## Four source-controlled 60-card tournament references

| Deck (2026 Aichi Open League) | Engine print/name/attack/Ability signatures | Physical copies | Finding |
| --- | ---: | ---: | --- |
| Champion Shadow Rider Calyrex VMAX | 32/33 print signatures | 59/60 | `xy4-92` Battle Compressor printed full-name alias unresolved |
| Runner-up Vileplume control | 38/38 | 60/60 | All selected print signatures matched |
| Fifth Mew VMAX / Genesect V | 30/30 | 60/60 | All selected print signatures matched |
| Tenth Regidrago VSTAR | 35/36 | 59/60 | Same `xy4-92` Battle Compressor display-name discrepancy |

All four baseline tables sum to 60 cards and have independently checked English card print IDs in [`results/competitive_deck_baselines/README.md`](../competitive_deck_baselines/README.md). The audit uses the shared exact-print resolver in [`simulation/twinleaf/print-coverage.cjs`](../../simulation/twinleaf/print-coverage.cjs) to handle set codes, promo prefixes, Basic Energy display qualifications, attack/Ability-labelled variant names, and the Mew V Fusion Strike role tag. It then additionally compares the printed attack name sequence and verifies each printed Ability name among the engine implementation's powers.

The only print-name discrepancy occurs twice across these lists: **Battle Compressor Team Flare Gear**, `xy4-92`, versus the engine's **Battle Compressor**, set PHF number 92. Inspection of the bundled source print's principal rule text and pinned engine `battle-compressor.ts` shows the same instruction to discard up to three searched deck cards and shuffle. The print-ID and effect agreement suggests a display-name alias, but the conservative classifier currently records `name_mismatch_review` until a narrowly grounded alias is adopted. No general name substitution is permitted.

## Interpretation

These numbers measure **static compatibility with candidate engine implementations**, not competitive strength or behavioral fidelity. Engine attack/Ability names can match while effects are wrong. One independently detected example is Shadow Rider's Underworld Door: the pinned ability implementation can offer a non-Psychic Bench target. See [`results/twinleaf_shadow_rider_underworld_door/README.md`](../twinleaf_shadow_rider_underworld_door/README.md) and the research-owned hook. Therefore even the two fully covered 60-card lists cannot yet be declared simulation-accurate.

The per-print JSON diagnostics can be retrieved from the workflow artifact `twinleaf-print-coverage` attached to [green run 38246939386](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38246939386) while retained. Strict 60-card engine registration for Vileplume and Mew/Genesect passed; paired native Store setup reached turn one in seven action dispatches per seat order (seeds 20261012 and 20261013). These tests verify startup with complete source-controlled lists and stop before matchup performance assessment. To reproduce, invoke the manual workflow `validate-twinleaf-expanded-bot.yml`, which compiles the pinned Twinleaf server and runs [`test-tournament-print-audit.cjs`](../../simulation/twinleaf/test-tournament-print-audit.cjs). The script also tests malformed deck detection, a matching synthetic Ability/attack signature, and a missing-print classification.

**Next decisions:** ground or explicitly reject the one Battle Compressor alias; exercise the Shadow Rider hook in CI and full board contexts; run bounded seeded paired-seat games using real 60-card decks with per-card behavioral audits. Retain separate labels for simulation-only smoke results, behavioral-validity tests, and actual match-performance evidence.
