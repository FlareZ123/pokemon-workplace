# Twinleaf live-game vs counterfactual-policy RNG isolation

**Status:** Pinned-engine diagnostic and a tested research-runner fix. **No competitive win-rate claim.**

## Question

Does Twinleaf's research headless match runner let `SimpleTacticsAi` counterfactual action evaluation consume the same seeded pseudorandom stream as **live** shuffles, coin flips and card effects? If so, can the research runner isolate those draws without modifying the pinned vendor submodule?

## Input provenance and reproduction

- Paper-deck sources: complete Aichi 2026 Vileplume and Mew/Genesect lists in [competitive deck baselines](../competitive_deck_baselines/); a separately mapped Aichi Mega Absol/Garbodor list in the current research-side runner.
- Twinleaf vendor pin: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.
- Runner: [`simulation/twinleaf/tournament-bounded-match.cjs`](../../simulation/twinleaf/tournament-bounded-match.cjs), physical trace seed `20261012`, identical paired seat swapping, at most 350 actions and 25 seconds per game. Absol's caller supplies a 20-second cap.
- Bot: pinned `SimpleTacticsAi`, with unvalidated strategy and internal `Simulator` lookahead. Arbiter: research-owned uniform Fisher-Yates shuffle, random coin flips. Official paper-card behavior is not certified end to end.
- Reproducer: run [`test-random-stream-ledger.cjs`](../../simulation/twinleaf/test-random-stream-ledger.cjs) with Node 20; the [manual pinned-engine workflow](../../.github/workflows/validate-twinleaf-expanded-bot.yml) also executes the complete mapped-deck diagnostics.
- [Pre-isolation CI, run 38291450937](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291450937) and [post-isolation CI, run 38292013716](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292013716).

## Failure mechanism and source audit

The original research runner set `Math.random` to one seeded Mulberry32 generator. Calls from live `BotArbiter` prompt handling and `Store.dispatch` used it as expected. But speculative `SimpleTacticsAi.decodeNextAction` also consumed values from that **same** stream through its hypothetical `Simulator` evaluations.

The pinned upstream [SimpleTacticsAi source](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/simple-bot/simple-tactics-ai.ts) delegates to tactics that simulate candidate actions. [SimpleTactic source](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/simple-bot/simple-tactics/simple-tactics.ts) constructs a fresh `Simulator`, dispatches candidates and resolves prompts. The upstream simulator uses its own `BotArbiter`; pinned `defaultArbiterOptions` have all-heads / no-shuffle lookahead, unlike physical-run random arbitration. This discrepancy is an *additional* bot-policy-model issue outside this fix.

The original trace and its identical seed after instrumenting `Math.random` revealed the following event-source draw counts:

| Runner and seat order | All draws | Setup | Live arbiter | Policy lookahead | Live dispatch | Termination |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Vileplume / Mew | 554 | 0 | 513 | 30 | 11 | Finished, seat 1 |
| Mew / Vileplume | 196 | 0 | 192 | 2 | 2 | Finished, seat 1 |
| Mega Absol self-play | 793 | 0 | 119 | 662 | 12 | Wall-time cap, unfinished |

The Mega Absol diagnostic consumed **662 of 793** tracked values while evaluating candidate actions. Its later physical PRNG values therefore depended on how much speculative exploration was performed. This is a deterministic replay comparability defect. These counts alone do not quantify bias in win rates.

## Implemented fix

[`random-stream-ledger.cjs`](../../simulation/twinleaf/random-stream-ledger.cjs) provides **separately advanced deterministic PRNG streams**:

- `game`: the original seed's Mulberry32 state, advanced by live setup, arbiter and dispatch only.
- `policy`: a separate Mulberry32 state derived from `seed ^ 0x9e3779b9`, advanced by speculative `decodeNextAction` only.
- A synchronous `track(source, callback)` wrapper restores the prior lane even when the callback throws.
- `snapshot()` reconciles per-source draw counts with game and policy stream counts. The match trace records `random_stream_policy='separated_live_game_and_counterfactual_policy_v1'`.

The [test SFT](../../simulation/twinleaf/test-random-stream-ledger.cjs) checks that the first 64 physical draws exactly equal the old seeded generator without intervening policy draws; after 700 policy draws, the 65th physical draw remains identical to an untouched control game stream. It also checks count invariants, invalid sources and exception-safe lane restoration.

These two pseudorandom streams are deliberately isolated in **state advancement**; they are still reproducible mathematical sequences derived from a common seed. No statistical independence or cryptographic security is asserted.

## Post-fix run results

| Runner and seat order | All draws | Physical-game draws | Policy draws | Termination |
| --- | ---: | ---: | ---: | --- |
| Vileplume / Mew | 495 | 479 | 16 | Finished, seat 1 |
| Mew / Vileplume | 198 | 195 | 3 | Finished, seat 1 |
| Mega Absol self-play | 792 | 131 | 661 | Wall-time cap, unfinished |

In both completed Vileplume/Mew traces the winner remains seat 1 under the selected seed and unsophisticated bot. The different total counts and transitions under the new stream policy are **expected**: source isolation changes subsequent random outcomes and possibly the policy's decisions. Results across the two RNG policies are incompatible as paired-game samples.

CI [38292013716](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292013716) passed the lane SFT, mapped 60-card validations, real first-turn setup, paired match probes, and Mega Absol bounded diagnostic.

## Remaining threats and next actions

1. **Match randomness:** one seed and two orientations provide no usable confidence about deck strength or seat advantage; match policies remain a much larger error source.
2. **Policy simulation:** hypothetical tactics use all-heads / no-shuffle whereas the live physical game uses random flips and uniform shuffles. This can produce optimistic or pessimistic candidate valuation. Quantify and repair through a pinned research-side policy adapter or a source-grounded evaluator.
3. **Hidden information:** audit what the cloned `State` leaks about unrevealed deck and opposing hand cards to bot policy and whether it influences action choices.
4. **Engine semantic coverage:** tested upstream Night Watch incorrectly lets the attacker select cards that should be random; Underworld Door also needs a target-validation hook. Integrate each verified research-side hook before attempting varied-field win-rate studies.
5. **Paired experimental design:** separate physical chance seeds and policy seeds from deck orientations and clearly record bot and hook versions. A paired seat swap with the same PRNG seed does not guarantee identical physical random events.

**Confidence:** High in the observed seed-stream coupling and in the isolated-lane SFT; limited to the pinned runner. Low in any competitive conclusion from the bot's match winners.
