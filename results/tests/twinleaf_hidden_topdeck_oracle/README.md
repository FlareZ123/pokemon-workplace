# Hidden-deck oracle in pinned Twinleaf SimpleTacticsAi

**Confirmed source and engine regression.** Pin: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. This finding is about decision-policy information leakage, not paper Expanded win rate.

## Mechanism

The repository's current `SimpleTacticsAi` policy examines possible Items by using `PlayTrainerTactic.evaluateAction`. Pinned `simple-tactics.ts` dispatches each candidate through `Simulator(state)` and resolves its search prompts. Pinned `simulator.ts` deep-clones the complete authoritative `State`, including the **actual unrevealed order** of each deck. The bot can value a search action using its secret result before the real player knows that result.

This affects an actual tournament reference: the [2026 Aichi fifth-place Mew/Genesect list](../../decks/mew-genesect/) runs **three Trainers' Mail**, ROS 92, which looks at the top four cards. Pokégear 3.0 supplies an independent top-seven example.

## Controlled native-engine experiment

The [standalone runnable test](../../../simulation/twinleaf/test-hidden-topdeck-oracle.cjs) uses pinned card implementations, native `PlayTrainerTactic`, prompt resolvers, and state scores. It constructs two otherwise identical 60-card-conserving states (including each player's deck, hand, Prizes and Active). The active attacker is Regidrago V, the actor holds a search Item and six Grass Energy, and both hidden deck inventories are identical. The only changed fact is the hidden position of Boss's Orders: first card versus eleventh card in deck.

| Held Item | Supporter secretly first | Supporter secretly eleventh |
| --- | --- | --- |
| Pokégear 3.0 | `PLAY_CARD_ACTION` | no action |
| Trainers' Mail ROS 92 | `PLAY_CARD_ACTION` | no action |

The test asserts matching visible observations, matching complete deck multisets, 60 physical cards for each side, and different native decisions solely as a function of undisclosed card order.

### Exhaustive private-position audit

The regression additionally enumerates **all 46 possible positions** of the single Boss's Orders in the 46-card remaining deck, separately for both Items (92 native tactic decisions). It proves exact correspondence between the Item's secret search window and the native decision:

| Item | Plays on positions | Holds on positions | Conditional play probability with a uniform random hidden order |
| --- | --- | --- | --- |
| Pokégear 3.0 | 7/46 | 39/46 | 15.2173913043% |
| Trainers' Mail | 4/46 | 42/46 | 8.6956521739% |

A real player selecting whether to use the Item before a new observation cannot condition that decision on the unseen position. In this example, native foresight achieves each card's hit probability while paying the Item cost **only in the hit worlds**. This is a controlled resource-payment distortion, not a calculated match-win advantage.

**CI passed:** [exhaustive run 38301300891](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301300891), superseding [initial two-world 60-card run 38300915037](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38300915037). The [manual-only workflow](../../../.github/workflows/validate-twinleaf-hidden-order-oracle.yml) pins Node 20.19.0 and the exact vendor revision, installs dependencies, and executes both cases without touching upstream.

## Interpretation and implications

This proves that the pinned native bot is **not observation-invariant**. Its full-game winners are currently suitable as engine diagnostics only. They must not be promoted to competitive Expanded win-rate evidence until the simulator policy's hidden-information boundary is corrected and revalidated.

The fixture enters a controlled midgame `State` directly; it does not report the prevalence or size of this leak over a tournament field. The result does not establish which deck benefits most, nor does it imply that the underlying Pokégear or Trainers' Mail engine effect itself is incorrect. Separating live and speculative RNG streams is already useful, but cannot fix a true hidden-order oracle.

**Next:** condition action evaluation on the player's accessible observations. A future policy must account for K0 versus K1 Prize knowledge, partially known deck positions and opponent-private state. A valid invariance regression should demand identical action distributions between worlds that the acting player cannot distinguish. Compare decks head to head only after decision-policy and card-semantic coverage checks. This implementation remained outside the vendor submodule.
