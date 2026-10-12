# Shadow Rider Calyrex VMAX: Underworld Door target-legality defect and research-side guard

**Status (2026-10-12):** Source-confirmed defect at pinned Twinleaf revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5`; the targeted engine regression and runtime hook [passed CI run 38246939386](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38246939386). This is a simulator-compatibility finding, not a measured deck advantage.

## Rules and implemented path

The actual `Shadow Rider Calyrex VMAX` (Chilling Reign `swsh6-75`) Underworld Door Ability attaches a Psychic Energy card from hand to **one of your Benched Psychic Pokémon** and draws two cards if attached. Target type is a hard eligibility constraint.

In the pinned Twinleaf source `ptcg-server/src/sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-vmax.ts`, the ability iterates `player.bench` as `card` and checks `card instanceof PokemonCard` before calling `pokemonHasCardType`. But each entry is a `PokemonCardList` object, so no Bench Pokémon is correctly classified by this test. Worse, the resulting Bench indices are supplied to `new AttachEnergyPrompt(...,{ blocked: blocked })`. In `ptcg-server/src/game/store/prompts/attach-energy-prompt.ts`, `options.blocked` means **indices of Energy cards in the source hand**, while `options.blockedTo` denotes destination slots. The prompt's default `validate()` does not independently enforce Pokémon target types.

Consequently the baseline implementation's prompt accepts a valid Psychic Energy from hand assigned to a non-Psychic Benched Pokémon. This improperly expands board acceleration routes and could distort matchup results for the 2026 Aichi champion Shadow Rider deck.

## Remedy without upstream edits

Research-owned hook: [`simulation/twinleaf/hooks/shadow-rider-underworld-door.cjs`](../../simulation/twinleaf/hooks/shadow-rider-underworld-door.cjs).

It intercepts only the Underworld Door PowerEffect in the research runtime, finds non-Psychic or empty Bench destinations using the actual slot's `getPokemonCard()`, adds those slots to `blockedTo` for bot/UI selection, and wraps `AttachEnergyPrompt.validate` to reject non-Psychic destinations even if supplied by a scripted client. The installer is idempotent, uses the existing engine class and prompt interfaces, and preserves normal Energy selection, Ability timing, and existing card effects. It leaves vendor code and the pinned Gitlink unchanged.

Targeted regression: [`simulation/twinleaf/test-underworld-door-targets.cjs`](../../simulation/twinleaf/test-underworld-door-targets.cjs). It constructs a live pinned engine Ability prompt with a Psychic and a Dragon Bench target. Its assertions confirm that the baseline permits the incorrect Dragon assignment, the hook rejects that assignment, the Psychic assignment remains permitted, and second installation is a no-op. The manual Twinleaf workflow exercised this SFT after compilation and passed: the unpatched prompt accepted an invalid Dragon Bench attachment; the patched prompt rejected it while accepting a Psychic Bench target; duplicate installation remained idempotent. The CI run also completed the real-bot setup smoke after cleaning up and exiting the standalone process.

## Limits and next evidence

This guards the identified target legality fault in the headless research process when the hook installer runs. It does not establish behavioral parity for Underworld Door in all circumstances, nor comprehensive Expanded card support. Any future runner using Shadow Rider must explicitly install the hook and record that fact in experiment metadata. If the upstream pinned implementation changes, the baseline-defect assertion must be reassessed before carrying the hook forward. More game-state and turn-sequencing tests are needed before interpreting match win rates.
