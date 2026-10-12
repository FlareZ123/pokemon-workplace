# Asymmetric reaction locks and the Garbotoxin self-conflict

## Source-grounded mechanism

[The Mega Scrafty counter-stack study](../reactive_counter_stack_frontier/) yields a theoretical 29 damage counters after a positive opponent-Pokémon attack: 5 from Mega Scrafty ex `me2pt5-135`, 4 from four Benched Spiritomb `me1-87`, 8 from four attached Spiky Energy `sv9-159`, and 12 from Deluxe Bomb `sv7-134`. These sources operate in separate Ability, Energy, and Tool channels.

The rules and exact print texts establish different suppression scopes:

- **Path to the Peak** `swsh6-148`: suppresses the Rule Box Mega Scrafty Ability while leaving non-Rule-Box Spiritomb functioning.
- **Wobbuffet** `xy4-36`: its Active Bide Barricade suppresses both Darkness Pokémon's Abilities because its exemption is for Psychic Pokémon.
- **Garbodor** `bw11-68`: an enabled Garbotoxin with a Pokémon Tool attached suppresses both Ability families. This can be **your own Garbodor**, so it defeats a Pokémon player's own counterattack plan.
- **Jamming Tower** `sv6-153`: turns off the attached Deluxe Bomb's Tool effect while leaving Energy/Abilities untouched. An attached Tool remains physically attached with its effect suppressed, so Jamming Tower does not by itself deactivate Garbotoxin's *Tool attached* condition.

The profile accepts lock-active facts and evaluates a post-attack-effects, pre-Knock-Out reaction window. An upstream game-state engine must verify source presence, immunity, Energy survival, Ability status, attack origin, and timing.

## Exact counter totals

| Profile | Full four-Spiritomb/four-Spiky/Deluxe | Mega Scrafty + Deluxe only |
| --- | ---: | ---: |
| Unlocked | **29** | **17** |
| Path to the Peak | 24 | 12 |
| Active Wobbuffet | 20 | 12 |
| Garbotoxin | 20 | 12 |
| Jamming Tower | 17 | 5 |
| Path + Jamming | 12 | 0 |
| Garbotoxin + Jamming | **8** | **0** |
| Garbotoxin + Path | 20 | 12 |

With four Spiritomb and Deluxe Bomb, reaching 170 counters requires zero Spiky in the unlocked case, one under Path, three under Garbotoxin or Wobbuffet, and four under Jamming Tower. It is impossible with four copies under Garbotoxin plus Jamming.

## Actual eighth-place Aichi baseline creates two collisions

The [published 2026 Aichi Mega Absol/Garbodor 60](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) contains two Garbodor and four Float Stone, providing the Garbotoxin lock package. Its ACE SPEC is **Secret Box** `sv6-163`. Deluxe Bomb cannot be added alongside Secret Box under the one-ACE-SPEC rule; a replacement costs the existing cross-category search connector. Leaving Garbotoxin enabled simultaneously suppresses both Scrafty and Spiritomb Abilities, removing nine potential damage counters from the maximum.

Thus importing the card package at face value into the Garbotoxin archetype is mechanically self-defeating unless the board and strategic lock policy are redesigned. No completed hybrid 60 or matchup win rate is claimed. Deliberately switching off Garbotoxin has its own opportunity cost.

## Reproduction and limits

Run `python results/reactive_counter_lock_profiles/reproduce.py`. It source-checks the four lock prints and five reaction prints, verifies the real 60-card Aichi manifest including Secret Box, and exhaustively compares source-by-source counts across 0–4 Spiritomb, 0–4 Spiky and three Tool choices. CI: `.github/workflows/validate-reactive-counter-lock-profiles.yml`.

The supplied Advanced Player's Rulebook, sections A-02, B-02, E-03 and damage-reactive effects, governs the timing distinction. Source eligibility is a caller obligation; this pure layer cannot certify a particular game state or winning strategy.
