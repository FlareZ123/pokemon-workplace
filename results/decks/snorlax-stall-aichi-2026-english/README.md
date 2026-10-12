# Snorlax Stall: 2026 Aichi third-place English adaptation

**Provenance:** Haruto Miki placed **third** at the [2026 CL Aichi Open League](https://limitlesstcg.com/tournaments/566/decklists), May 10, among 926 players, with a Japanese 60-card Snorlax Stall control list. This page is a fully specified, **experimental English-print adaptation** of that historical source. Japan's list contained one **Player's Ceremony**, which is not available as a selected legal English printing in the provided pool. This candidate removes that Japanese-only Stadium and adds a second **Tropical Beach** `bwp-BW28`. It retains the other **59 cards** by name and quantity. **The third-place finish is the source deck's achievement; the substitute English variant has no tested tournament or match-win record.**

## Complete playable 60

### Pokémon (11)

| Qty | Card | English print |
| ---: | --- | --- |
| 3 | Snorlax | `bw8-101` |
| 2 | Galarian Stunfisk | `swsh1-132` |
| 1 | Regirock | `xy7-40` |
| 1 | Mimikyu | `sv2-97` |
| 1 | Girafarig | `sm8-94` |
| 1 | Bunnelby | `xy5-121` |
| 1 | Articuno-GX | `sm7-31` |
| 1 | Rotom V | `swsh11-58` |

### Trainers (44)

| Qty | Card | English print |
| ---: | --- | --- |
| 4 | Plumeria | `sm3-120` |
| 4 | Arven | `sv1-166` |
| 2 | Team Flare Grunt | `xy1-129` |
| 2 | Teammates | `xy5-141` |
| 2 | Lusamine | `sm4-96` |
| 1 | Team Rocket's Handiwork | `xy10-112` |
| 1 | Gladion | `sm4-95` |
| 1 | Guzma | `sm3-115` |
| 1 | Faba | `sm8-173` |
| 1 | Penny | `sv1-183` |
| 1 | Eri | `sv5-146` |
| 1 | Lillie's Determination | `me1-119` |
| 3 | Nest Ball | `sv1-181` |
| 3 | VS Seeker | `xy6-110` |
| 2 | Enhanced Hammer | `sv6-148` |
| 2 | Trainers' Mail | `xy6-92` |
| 2 | Counter Catcher | `sv4-160` |
| 1 | Scoop Up Cyclone | `sv6-162` |
| 1 | Quick Ball | `swsh1-179` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Night Stretcher | `sv6pt5-61` |
| 1 | Float Stone | `xy8-137` |
| 1 | Stealthy Hood | `sm10-186` |
| 1 | Tool Jammer | `swsh5-136` |
| 1 | Forest Seal Stone | `swsh12-156` |
| 2 | Tropical Beach | `bwp-BW28` |
| 1 | Temple of Sinnoh | `swsh10-155` |

### Energy (5)

| Qty | Card | English print |
| ---: | --- | --- |
| 3 | Capture Energy | `swsh2-171` |
| 2 | Water Energy | `bw1-107` |

**Total: 11 Pokémon + 44 Trainers + 5 Energy = 60 cards**, with 11 eligible Basic starters, one Scoop Up Cyclone ACE SPEC and two Tropical Beach Stadiums.

## Tactical identity and substitution rationale

**Active-position Snorlax Block:** Three `bw8-101` Snorlax have an Ability preventing the opponent's Active Pokémon from retreating while Snorlax itself is Active. This can strand a low-impact Pokémon, but switching effects remain legal and can free the opponent. Three Nest Ball and one Quick Ball provide some Basic Pokémon access, while two Counter Catcher and Guzma help manipulate opposing board positions.

**Resource denial:** Two Galarian Stunfisk `swsh1-132` retaliate with Snap Trap by discarding Energy from attackers when damaged while Active. Four Plumeria, two Team Flare Grunt, two Enhanced Hammer, one Faba and one Eri apply different discard and disruption resources, competing for Supporter turns. Single-Prize Mimikyu's Safeguard protects it from attack damage from opposing Pokémon ex and Pokémon V, subject to Ability suppression and bypass effects. Girafarig's Get Lost can send cards from the opposing discard pile to the Lost Zone. Bunnelby `xy5-121` uses Rototiller to recycle one discarded card; repeated turns of control must still avoid deck-out.

**Alternative finish or rescue routes:** Articuno-GX's Legendary Ascent can promote itself when Benched from hand, and Cold Crush-GX can clear both Active Pokémon's Energy. Rotom V's Instant Charge draws three and ends the turn, an option that also exposes a two-Prize liability. Scoop Up Cyclone can return one of the player's Pokémon and attached cards to hand, subject to real Active/Bench conditions.

**English Stadium substitution:** The original source used one Tropical Beach and one Player's Ceremony. This variation uses two Tropical Beach. Its once-a-turn optional draw to seven ends the turn if activated. That is substantively different from Player's Ceremony's end-turn draw-two effect, and can benefit either player. Tropical Beach is also a physically expensive older promo; real deck availability can be a practical constraint. The doubled Stadium has no independently demonstrated competitive superiority.

## Evidence and next tests

The [machine-readable manifest](manifest.json) preserves 37 English card prints and the one-name replacement. The [independent 60-card source/legality reproducer](../../tests/snorlax_2026_english_print/reproduce.py) checks the published card-name counts, all unchanged 59 source copies, category totals, 11 eligible Basic Pokémon, eight important exact printed attacks/Abilities, one ACE SPEC and conservative English Expanded eligibility as of October 12, 2026. Regional tournament approval is not separately established.

A useful next comparison is against Regidrago variants, Raichu/Electrode, Iron Thorns, Shadow Rider and Vileplume under a real deck-wide opponent distribution and explicitly modeled Item/Supporter lock, repeated gust, Energy denial and deck-out timing. Opening access or card-lock labels alone cannot establish how reliably control converts into a win.
