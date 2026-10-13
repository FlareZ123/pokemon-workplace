# Paper Expanded: random opponent-hand effects in pinned Twinleaf

**Date:** 2026-10-13. **Engine pin:** 3348ebdc898f175a2ed8f999133cd13d1afd01f5. **Evidence:** published English card text embedded in exact source implementation, live class regression, source-code audit, and pinned CI. **No full-match win-rate claim.**

## Motivation

The printed card instruction "choose a random card from your opponent's hand" demands an independent random physical card selection. In pinned Twinleaf, several reducers instead issue a ChooseCardsPrompt owned by the attacker, targeting the opponent's hand, with isSecret=true and min=max=1. That flag makes card faces secret in the prompt. It does **not** impose a uniform random choice over the allowable index set. The engine accepts every singleton hand index as a legal attacker action.

The [Night Watch random two-card case](../twinleaf_night_watch_live_hook/README.md) is especially relevant to the 2026 Aichi champion Shadow Rider Calyrex baseline, which contains Trevenant & Dusknoir-GX SMP217.

For a hand of n cards and k distinct strategically critical cards, the proper chance that uniform random two-card Night Watch hits at least one critical is 1 - C(n-k,2)/C(n,2). In a seven-card hand with one critical card, that is **2/7 = 28.571429%**. A fully informed chooser could select that critical card with certainty. This is a hypothetical extreme-gap illustration, not a measured bot advantage.

## Source audit and boundaries

A targeted GitHub code search of pinned upstream card reducers found 17 files containing both "random card" and ChooseCardsPrompt. That candidate-search procedure is **not an exhaustive search of every random-card mechanic** because alternative wording and implementation patterns can escape the query. Manual code review separated two direct-random implementations (Persian NXD and Ambipom LOR) and one non-Expanded Mankey Jungle with an unrelated ChooseCardsPrompt from 14 problematic Expanded reducer candidates.

Of those 14:
- **11 cards now have a research-side random-selection correction:** ten single-card prompts listed below and Night Watch's two-card prompt.
- **Three cards remain specialized source defects:** Dusclops BCR62 (generator-driven attacker choice), Honchkrow UPR72 (reversed empty-hand condition), and Wimpod PAR48 (coin flip fails to gate later choice).

The three specialized cases must be handled separately. The current ten-card hook deliberately excludes them and reports only the ten classes it actually protects.

### Ten patched single-card exact prints

| Print | Effect | Original source problem |
| --- | --- | --- |
| Tormenting Spray BUS125 | Random hand reveal and discard only if Supporter | Attacker-owned secret chooser |
| Gothitelle PAL92, Psych Out | Random hand discard | Attacker-owned secret chooser |
| Tyranitar ex PRE64, Tyranical Crush | Random hand discard | Attacker-owned secret chooser |
| Murkrow UNB108, Astonish | Random hand shuffle-back | Attacker-owned secret chooser |
| Sandygast CEC126, Astonish | Random hand shuffle-back | Attacker-owned secret chooser |
| Zubat SUM54, Astonish | Random hand shuffle-back | Attacker-owned secret chooser |
| Lotad CES36, Surprise | Random hand shuffle-back | Attacker-owned secret chooser |
| Pumpkaboo CIN44, Astonish | Random hand shuffle-back | Attacker-owned secret chooser |
| Togepi OBF83, Whiny Voice | Random hand shuffle-back | Attacker-owned secret chooser |
| Jynx SLG38, Whiny Voice | Random hand shuffle-back | Attacker-owned secret chooser |

[Research-owned adapter](../../../simulation/twinleaf/random-hand-single-card-hook.cjs) uses exact compiled class identities, active AttackEffect or TrainerEffect matching, and the one required ChooseCardsPrompt over the opponent's hand. It intercepts that prompt only, uses a uniform RNG draw of the actual Card object and invokes the original reducer callback. All existing card movement, conditional Supporter handling, reveal and shuffle remain owned by the upstream reducer.

The adapter is reversible and idempotent. It uses a late-bound game Math.random function so the existing live runner's seeded random-event ledger captures these stochastic decisions. Source edits remain outside the upstream Git submodule.

The [live bounded-match runner](../../../simulation/twinleaf/tournament-bounded-match.cjs) installs this guard and emits the version label random_hand_ten_single_card_prints_v1 in individual game traces and aggregate reports. Together with night_watch_uniform_discard_v1, **eleven known random hand source cases are guarded**. Previous raw simulated games lacking these labels must not be compared without an engine-version qualification.

### Three specialized unpatched bugs

**Honchkrow UPR72, Rip and Run:** The source checks if opponent.hand.cards.length === 0 before trying to choose and discard the random opposing hand card. Consequently, with a nonempty opposing hand and no Bench target, the printed discard does nothing. On an empty hand, the source attempts a one-card prompt over an empty hand. The expected flow is to discard a random card when one exists, then execute the attack's switch effect if possible.

**Wimpod PAR48, Sneaky Snacking:** The source schedules a coin flip whose callback returns early on tails, but schedules ChooseCardsPrompt **outside that callback**. An explicit tails-result controlled test still records an attacker hand-discard chooser. A repair must gate the entire discard branch on heads.

**Dusclops BCR62, Astonish:** The source uses a generator that yields an attacker-owned secret one-card choice. The normal one-card synchronous callback interceptor cannot safely be reused because its callback resumes the generator. A specific adapter or a prompt-level scheduling repair must preserve the generator sequence and the reveal/shuffle tail.

### Independent behaviors that should not be misclassified

Persian NXD Shadow Claw and Ambipom LOR use Math.random to choose the physical opponent-hand card in their relevant random-discard attacks. Their separate ChooseCardsPrompt instances serve other card effects. Mankey Jungle is pre-Black-and-White and its random reveal also directly samples with Math.random. Hooligans Jim & Cas DEX, found with a different text search, already samples without replacement directly in source; it is excluded from this error list.

## Executable evidence and coverage limits

- [Ten-card source reducer SFT](../../../simulation/twinleaf/test-random-hand-single-hook.cjs): authentic compiled card class per exact print, physical three-card opposing hand, each of three equiprobable RNG bins selecting its corresponding physical object, intact source movement/reveal/shuffle/conditional behavior. Thirty card-effect cases, plus idempotence.
- [Three-special-case source-gap witness](../../../simulation/twinleaf/test-random-hand-source-gaps.cjs): directly executes Honchkrow nonempty hand, Wimpod after forced tails, and Tormenting Spray attacker-owned prompt. These tests document old defects and will need revised expected outcomes if the remaining cards are fixed.
- [Night Watch SFT](../../../simulation/twinleaf/test-night-watch-live-hook.cjs) and [real Store SFT](../../../simulation/twinleaf/test-night-watch-real-store.cjs): two-card uniformity through 3/5/7 hand sizes, physical movement, original source reveal/shuffle prompts and real pinned Store integration.
- [Live runner integration test](../../../simulation/twinleaf/test-tournament-engine-hooks.cjs): ensures patch installation and version labels during actual seeded runOne() invocation.
- [Focused compiled-engine CI 38333033380](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38333033380): **PASSED** all source-reducer, source-gap, and live runner tests.

No evidence here establishes that all random-hand effects in the entire Expanded card pool are covered, that Twinleaf implements every rule correctly, or that its native decision policy yields competitive matchup estimates. The prior [hidden-order bot oracle diagnosis](../twinleaf_hidden_topdeck_oracle/README.md) remains an independent barrier.

## Research follow-up

Prioritize standalone, narrowly scoped corrections for Honchkrow's empty-hand guard, Wimpod's coin-gate and Dusclops's generator callback. Add source-pinned physical/reaction tests for each. Consider a broader card-pool audit using AST-aware classification and print legality checks, as search snippets alone are insufficient to claim completeness.
