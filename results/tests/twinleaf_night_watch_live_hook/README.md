# Twinleaf: Night Watch randomized opponent-hand discard installed in live Aichi matches

**Evidence types:** card text, source inspection at pinned Twinleaf revision, physical-card reducer regression, live-runner hook assertion. This diagnoses and repairs one engine mismatch; it does not establish competitive win rates.

## Concrete defect and card relevance

The published 2026 Aichi Expanded champion Shadow Rider Calyrex deck includes one Trevenant & Dusknoir-GX (English equivalent SMP SM217). Its Night Watch attack does 150 damage and randomly selects two cards from the opponent's hand, which are revealed and shuffled into their deck.

At the pinned upstream revision 3348ebdc898f175a2ed8f999133cd13d1afd01f5, the card reducer creates an attacker-owned ChooseCardsPrompt over the opponent's actual hand with min=max=2 and isSecret=true. That prompt accepts all two-card index pairs. Neither card source nor prompt enforces a uniform distribution. An automated player's chosen indices can therefore overfit the opponent's hidden identities or otherwise behave unlike random selection.

The earlier independent source-reducer witness is [test-night-watch-randomness.cjs](../../../simulation/twinleaf/test-night-watch-randomness.cjs). Source is pinned in the upstream repository, which remains unmodified.

## Existing research hook, now installed in matches

The already-existing [reversible hook](../../../simulation/twinleaf/night-watch-random-hook.cjs) intercepts only this card's initial, exact two-card ChooseCardsPrompt. It samples the actual Card objects via a partial Fisher-Yates shuffle, taking k=min(2, opponent hand size), then immediately resolves the source reducer's original callback with the chosen cards. That callback retains its existing MOVE_CARDS, ShowCardsPrompt and ShuffleDeckPrompt tail.

[The bounded-match runner](../../../simulation/twinleaf/tournament-bounded-match.cjs) now installs this hook in ensureResearchEngineHooks() along with the verified Underworld Door, Celestial Roar and Stoutland compatibility guards. The installation uses random:()=>Math.random(). That deferred lookup is intentional. runOne installs engine hooks **before** it swaps Math.random to its seeded game-event RNG stream; capturing the current RNG function while installing would silently detach Night Watch from game seed control.

The every-game engine hook provenance gains a fourth string: night_watch_uniform_discard_v1. This applies to both per-game traces and the aggregate matchup report. Prior traces lacking this label should not be pooled with newer runs as though the engine semantics were identical.

## Regression specification

[Focused CJS SFT](../../../simulation/twinleaf/test-night-watch-live-hook.cjs) invokes the actual printed Night Watch reducer after installing the hook through the same ensureResearchEngineHooks() function as live matches. A minimal controlled Store exposes authentic Player, CardList, AttackEffect and MoveCardsEffect objects, executes physical card moves through CardList.moveCardsTo, and records the actual reveal/shuffle prompts.

Its assertions cover:

- Exactly two separate physical cards moved from opponent hand to deck when at least two are available.
- The revealed two objects have the same physical identities as the moved pair, and the original shuffle prompt is requested.
- The attacker never receives an executable ChooseCardsPrompt for Night Watch's randomized hand selection.
- With three distinct opposing hand cards, a 3-by-2 partition of six equiprobable RNG bins produces all three unordered pairs exactly twice, agreeing with the 1/3-per-pair distribution.
- One-card and empty-hand boundary cases preserve the correct physical count.
- The RNG function is resolved dynamically at actual attack time; the same hook is idempotent across repeated installations.

The [live-runner hook SFT](../../../simulation/twinleaf/test-tournament-engine-hooks.cjs) additionally checks that real runOne() calls install all four hook markers and expose their version labels.

A new small workflow [validate-twinleaf-night-watch-live.yml](../../../.github/workflows/validate-twinleaf-night-watch-live.yml) checks out only the pinned submodule, compiles if needed, then runs these focused SFTs. The manual paired-matchup workflow also runs the focused Night Watch SFT before starting games.

## Limitations and model implications

The SFT uses a controlled Store effect adapter to assert physical move semantics and original reducer callbacks; the live runner SFT verifies installation but its tiny synthetic match need not reach Night Watch. An independent end-to-end attack-triggered Store match fixture would strengthen confidence further.

Card-specific changes are confined to research-owned hooks. They are source-pinned: if the Twinleaf gitlink advances, rerun semantic and engine integration tests before treating this patch as compatible.

The headless SimpleTacticsAi policy has independently documented hidden deck-order observation weaknesses and insufficient competitive playing strength. This repair closes a real stochastic fairness gap in one Aichi list and contributes to future engine-valid match data, while matchup results remain policy- and coverage-dependent.
