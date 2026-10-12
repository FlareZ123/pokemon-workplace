# Pinned Twinleaf chance modeling: modern CoinFlipEffect vs legacy CoinFlipPrompt

**Question:** Does `SimpleTacticsAi`'s default `BotArbiter` setting `ALL_HEADS` make hypothetical Pokémon Catcher flips succeed deterministically? **Answer for the verified SVI 187 card: no.** The pinned engine has two distinct coin-resolution pathways with different arbitration semantics.

## Actual source and reproducible evidence

- Vendor engine: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.
- Research-side native SFT: [`simulation/twinleaf/test-counterfactual-coin-model.cjs`](../../../simulation/twinleaf/test-counterfactual-coin-model.cjs).
- [Full pinned-engine CI 38294095876](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294095876): **success**. The run also passed full 60-card Aichi deck mapping, RNG stream isolation, and Vileplume/Mew seat-paired diagnostics.
- [Pokémon Catcher SVI 187 engine class](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/sets/10-scarlet-and-violet/set-scarlet-and-violet/pokemon-catcher.ts) uses `COIN_FLIP_PROMPT`, which wraps `CoinFlipEffect`.
- [Pinned `RESOLVE_COIN_FLIP_EFFECT`](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/game/store/prefabs/attack-coin-reflip.ts) calls `Math.random() < 0.5`, records the result, and produces a `WaitPrompt` for the animation before advancing the callback.
- [Pinned `BotArbiter`](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/game/bots/bot-arbiter.ts) instead handles `CoinFlipPrompt`. `defaultArbiterOptions` choose `ALL_HEADS` and `NO_SHUFFLE`. The `RANDOM` flip mode samples the current random source.

The standalone test builds a native `State` on turn four. An actual SVI Pokémon Catcher is played against an opposing Regidrago V on the Bench, followed by native prompt resolution including the coin-animation `WaitPrompt`. The controlled `Math.random` input is 0.1 (heads) or 0.9 (tails). Four independent replays use both default and explicitly randomized `Simulator` arbitration options:

| Real SVI Catcher `CoinFlipEffect` | RNG=0.1 | RNG=0.9 |
| --- | --- | --- |
| Default `Simulator` options | Heads: gusted Regidrago V ID 102 | Tails: original Active ID 101 |
| `BotFlipMode.RANDOM` | Heads: gusted Regidrago V ID 102 | Tails: original Active ID 101 |

Each execution used exactly one random draw and one `WaitPrompt`. The native conditional choice prompt appears only on heads. Thus the default `ALL_HEADS` arbiter option **does not override this modern card-effect flip**, which is resolved by `Math.random` outside `BotArbiter.resolvePrompt`.

The same SFT instantiates a standalone **legacy `CoinFlipPrompt`**, feeds it directly into the native `BotArbiter`, and observes:

| Legacy prompt resolution | RNG=0.1 | RNG=0.9 |
| --- | --- | --- |
| Default `BotArbiter` | Heads | Heads |
| `BotFlipMode.RANDOM` | Heads | Tails |

This is a confirmed API semantic difference. The fixture is not asserting that the 2026 competitive Aichi card pool necessarily uses a legacy `CoinFlipPrompt` in a card effect.

A source search for `new CoinFlipPrompt` at the pinned revision found the actual creation in `ptcg-server/src/game/store/reducers/setup-reducer.ts` for the opening turn-order flip. This does not prove no dynamically generated or atypical paths exist, but prevents extrapolating legacy ALL_HEADS behavior to every coin-flip effect in a game.

## Practical consequence for deck research

The live-game RNG and the policy-lookahead RNG were separated in [the preceding RNG isolation work](../../twinleaf_rng_stream_isolation/). Consequently, modern `CoinFlipEffect` directly consumes **speculative RNG draws during policy simulations** under the isolated policy lane and draws from the physical-game lane only during real effects.

The verified card's two branches remain possible in hypothetical simulation. A single speculative sampled outcome is **not an expected-value estimate** for an action with 50/50 results. Action ranking may be noisy or affected by the order in which candidates are evaluated. Additionally, `NO_SHUFFLE` is still the default for arbitrated hypothetical shuffle prompts, unlike the physical game. The bot is not yet validated for real Expanded deck strength.

**Confidence:** High in the concrete two-path SFT and source locations; limited in any claim about aggregate chance-handling frequency, policy quality, or match outcomes.

## Next experiments

Inspect the exact `ShuffleDeckPrompt` emission paths used by search/draw cards, then test whether two strategically identical observed states with different hidden deck order cause a different `SimpleTacticsAi` action under the default `NO_SHUFFLE` lookahead. A valid policy must compare its options without unrealistically knowing unrevealed top-deck identities.
