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

## Additional real-Store confirmation and numerical risk context

[Manual CI run 38301157584](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301157584) passed the additional `test-regidrago-celestial-roar-store.cjs`. This exercise uses Twinleaf's actual `Store.reduceEffect`, native move-card handling and `CheckProvidedEnergyEffect`. With a prepared Regidrago V Active and a top-three reveal containing Double Dragon Energy, Basic Grass Energy, and a non-Energy card, the patched effect attaches both Energy cards and discards only the non-Energy. The resulting native energy map confirms that Double Dragon supplies **two `ANY` Energy units** to its Dragon recipient.

The reproducible exact blind-three composition census is [`reproduce.py`](reproduce.py), derived directly from the published 60-card JSON. With four Double Dragon, six Basic Energy and fifty non-Energy cards in an *untouched hypothetical 60*, a uniformly random three-card reveal contains at least one Double Dragon with probability **325/1711 = 18.994739918%**. The original Basic-only code misses an expected **1/5 Double Dragon cards** or **2/5 provided Energy units** per such reveal. The chance of at least one Energy of either category is **731/1711 = 42.723553477%**.

**Scope:** an untouched 60-card blind draw is a diagnostic null model. An actual Celestial Roar happens after a Basic-containing opening, six Prizes, card draw/search, and usually other setup decisions. The conditional probability of the bug affecting a *played* Celestial Roar depends on the resulting live deck composition and the policy's decision to attack. Neither the 18.99% nor the expected 0.4 units is a match win-rate estimate.

## Natural first-turn attack exposure with hand and Prize constraints

The basic 18.9947% blind-three composition figure above does not condition on an attack being legal. [`natural_first_attack.py`](natural_first_attack.py) models a stricter physical opening for the **published unchanged 60**, going second:

1. Seven random opening cards contain at least one Regidrago V, chosen as the starting Active. Other Basics may also be held.
2. Six Prize cards are set aside. The player draws one natural card at the start of their first turn.
3. At least one Energy card (four Double Dragon, four Basic Grass, or two Basic Fire) appears in the first eight exposed hand cards and may be manually attached to Regidrago V to pay Celestial Roar's Colorless cost.
4. Celestial Roar reveals the next three deck cards. Its corrected-versus-buggy outcome differs if at least one Double Dragon Energy appears among them.

No Switch, Ball, Supporter, mulligan bonus draw, Ability draw, Item action, opponent lock, attack policy or prior information is granted. The player has no need to perform a first deck search. This is a **natural, executable source-availability event** for one particular first-turn going-second line, without modeling the choice to take that line or its strategic utility.

The exact category solver enumerates all opening seven-card compositions, then conditions on the first natural draw. Six random Prize identities are *marginalized*, preserving their physical unavailability. Exchangeability makes the following three unknown cards a hypergeometric sample from the remaining 52 cards after the first draw, even though six of the 52 are Prized. An independent `labeled_physical_oracle` enumerates explicit original physical-card identities, 2-card Prize sets, first draws and 3-card reveals in two 10-card toy configurations; both exact events agree with the category solution.

| Event | Exact result | Percentage |
| --- | --- | ---: |
| Basic-valid opening, before mulligan conditioning | `172135/195054` | **88.249920535%** |
| Regidrago starting Active + Energy available for T1 Celestial Roar, unconditional | `1561585/5168931` | **30.210985598%** |
| Same turn-one source event, conditional on Basic-valid opening | `624634/1824631` | **34.233442269%** |
| Source event AND revealed Double Dragon Energy, unconditional | `315139423777/5654552067450` | **5.573198726%** |
| Source event AND revealed Double Dragon, conditional on Basic-valid opening | `315139423777/4990137706125` | **6.315245036%** |
| Revealed Double Dragon, conditional on the natural T1 source event | `315139423777/1708295910750` | **18.447589893%** |

Thus, across the **restricted naturally ready** turn-one Celestial Roar windows, **18.4476%** would reveal a Double Dragon Energy that the original engine incorrectly discards. This quantifies how frequently the confirmed semantic defect can affect a *physically available direct early attack*, not its probability in a played match or its effect on winning. The player might intentionally use a stronger line instead, and opponent-specific disruption can prevent the attack.

## Interpretation and remaining limits

Engine simulations recorded **before** this Regidrago correction silently use a different Energy-acceleration rule than the physical source card. Do not treat them as directly comparable to guarded results. Even guarded runs use `SimpleTacticsAi`, which can fail to select realistic attack, attachment or search choices. Confidence in those policy outcomes remains low.

The fix addresses all revealed card categories for Regidrago V's Celestial Roar, while more complex Special Energy interactions still require broad full-game tests. The target-specific Card/Special Energy semantics of other archetypes have not been comprehensively audited. This is an executable rules correction, not a recommended change to the published decklist.
