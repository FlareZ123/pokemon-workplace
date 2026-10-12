# Regidrago V Celestial Roar: Special Energy omitted by pinned Twinleaf

## Card-rule issue in a top-ten published deck

The source-validated [2026 Aichi tenth-place Regidrago VSTAR 60-card list](../../decks/regidrago-vstar/) plays **4 Double Dragon Energy** (`xy6-97`). Its Regidrago V (`swsh12-135`) can use **Celestial Roar** to discard the top three deck cards and attach *any Energy cards among them* to itself. This includes the four Special Double Dragon Energy copies, which can attach to Regidrago V because it is a Dragon Pokémon.

The pinned Twinleaf engine revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5` implements Celestial Roar in `ptcg-server/src/sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts` using a filter of `card.energyType === EnergyType.BASIC`. It only attaches those filtered Basic Energy cards. If the attack reveals Special Energy, the original implementation discards them rather than attaching them.

That underestimates immediate Regidrago Energy acceleration and can strongly distort the deck's attack readiness and full-game diagnostics. No real match win-rate effect is inferred.

## Research-side repair and reproducible test

The idempotent, source-pinned correction is [`simulation/twinleaf/hooks/regidrago-celestial-roar.cjs`](../../../simulation/twinleaf/hooks/regidrago-celestial-roar.cjs). On Celestial Roar it reveals up to three physical cards using the native `MOVE_CARDS` effect, attaches every `EnergyCard` instance to the attacking Dragon Pokémon, and sends the non-Energy cards to discard. It delegates all other Regidrago attacks and effects to the unchanged upstream implementation. The research-owned code does not modify the vendored git submodule.

The independent [single-file regression](../../../simulation/twinleaf/test-regidrago-celestial-roar.cjs) invokes the actual pinned Regidrago V attack reducer and native move effect types. It requires:

- the unpatched attack to mishandle revealed Double Dragon Energy, demonstrating the pinned implementation defect;
- the installed correction to attach a mixed Double Dragon + Grass Energy reveal, leaving the non-Energy card in discard;
- an all-Double-Dragon reveal to attach every Special Energy card;
- a no-Energy, short-deck reveal to discard its non-Energy cards correctly;
- conservation of physical card identity and idempotent installation.

A deliberately small `StoreLike` move-effect executor performs only the known native `CardList.moveCardsTo` physical mutation. This is a targeted card-effect regression; the separate live-match SFT supplies a full `Store` integration gate.

The standard bounded matchup runner [`tournament-bounded-match.cjs`](../../../simulation/twinleaf/tournament-bounded-match.cjs) now installs both this repair and the [Shadow Rider Underworld Door legality correction](../twinleaf_underworld_live_hook/) before a game begins. The per-game trace and aggregate report explicitly identify:

`engine_hooks: ["shadow_rider_underworld_door_guard_v1", "regidrago_celestial_roar_any_energy_v1"]`

Both manual Twinleaf workflows run the focused Regidrago SFT and live engine-hook SFT before their paired matchup samples. No upstream Twinleaf commit is changed.

## Confirmed CI execution

[Manual paired CI run 38300711450](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38300711450), 12 October 2026, passed all four relevant steps: the existing Underworld Door target check, the new Celestial Roar Special Energy regression, live-match automatic hook installation, and a bounded two-orientation Shadow Rider vs Regidrago game pair. The regression explicitly logged that the pinned unmodified Regidrago attack had discarded a revealed Double Dragon Energy; after installing the correction, its Basic, Special, all-Special, and no-Energy assertions passed.

Both paired seed-20261012 games finished under `SimpleTacticsAi`. The first finished at turn 20 after 131 actions; the second at turn 37 after 194 actions. Shadow Rider won both again. The trace reported both semantic hooks and no errors. The published reference's Regidrago bot used Celestial Roar three total times across these games, but the trace does not separately record which Energy types were revealed. Consequently the score repetition cannot establish the actual on-match impact of this defect.

## Interpretation and remaining limits

Engine simulations recorded **before** this Regidrago correction silently use a different Energy-acceleration rule than the physical source card. Do not treat them as directly comparable to guarded results. Even guarded runs use `SimpleTacticsAi`, which can fail to select realistic attack, attachment or search choices. Confidence in those policy outcomes remains low.

The fix addresses all revealed card categories for Regidrago V's Celestial Roar, while more complex Special Energy interactions still require broad full-game tests. The target-specific Card/Special Energy semantics of other archetypes have not been comprehensively audited. This is an executable rules correction, not a recommended change to the published decklist.
