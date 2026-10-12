# Aichi 2026 Raichu/Electrode: first-turn natural evolution-base seed

**Competitive deck:** [Shu Hosoda, 2026 Aichi Open League fourth-place 60](../../decks/raichu-electrode-aichi-2026/), based on the [published list](https://www.limitlesstcg.com/decks/list/26812).

This source-verified **natural material bound** isolates whether the opening seven cards plus one ordinary first-turn draw contain two distinct Basic Pokémon capable of later becoming Electrode-GX and Alolan Raichu. It is conditional on a valid Basic-containing opening seven, with no extra mulligan draw or other card effects. The six face-down Prize cards are marginalized exactly; conditioning on a valid opening seven, the first turn's draw is uniform among the 53 remaining physical cards.

## Source-checked mechanics

The representative 60-card list contains two Voltorb, one Pikachu, one Ditto Prism Star, nine other Basic Pokémon, and 47 non-Basic cards. Voltorb normally evolves into Electrode-GX; Pikachu into Alolan Raichu; Ditto Prism Star's Almighty Evolution can evolve into either Stage 1, subject to its own timing and Ability availability. One Ditto cannot satisfy both evolutions simultaneously. The two-source condition therefore is `(Voltorb and (Pikachu or Ditto)) or (Pikachu and Ditto)`.

The supplied advanced manual states that neither player can evolve Pokémon on their first turn. Ditto Prism Star itself says Almighty Evolution cannot be used during its first turn or the turn Ditto entered play. With the published list's represented ordinary evolution route, Electrode-GX plus Alolan Raichu cannot both be evolved and launch Electro Rain on the first turn, regardless of going first or second. **Earliest possible normal own turn is turn 2**, assuming both Basic bases were established on turn 1 and the Evolution Pokémon, acceleration material, and attack Energy are accessible on turn 2.

Klefki `sv1-96` has Mischievous Lock: when in the Active Spot, Basic Pokémon in play have no Abilities other than Mischievous Lock. This suppresses its owner's unevolved Ditto Prism Star Almighty Evolution. Before attempting a Ditto evolution, a Klefki-Active line must remove the suppression or find a different evolution route.

## Exact physical-card probabilities

| Event | Exact conditional probability | Percentage |
| --- | --- | ---: |
| Initial seven contains any Basic (unconditional) | `1 - C(47,7)/C(60,7)` | **83.715595%** |
| Two distinct evolution-source Basics in initial seven, given valid seven | `20595960/323315421` | **6.370237%** |
| Two distinct source Basics after first normal draw, given valid seven | `814128/9797437` | **8.309602%** |
| Native Voltorb and Pikachu both available after that draw, given valid seven | `351120/9797437` | **3.583794%** |
| Two-source condition holds only with Ditto, given valid seven | `463008/9797437` | **4.725807%** |

Of qualifying eight-card natural seed events, **56.871647% need Ditto** to provide one of the two different Stage 1 source Basics. If Klefki is Active throughout the evolution turn and its Ability lock is uninterrupted, these Ditto-dependent states cannot execute Ditto's evolution Ability in that state.

The SFT evaluates both a closed-form combinatorial identity and independent exhaustive hand-multiplicity enumeration. For eight observed physical cards, the two-source event count is:

`C(60,8) - C(58,8) - 2*C(56,7)`.

Divide its probability in a random eight by the probability of a valid initial seven. Any eight-card hand satisfying the two-source condition must have started from a valid seven, since a single subsequent card cannot create two distinct eligible Basic role categories.

## Reproduce

Run `python results/tests/raichu_2026_natural_seed/reproduce.py`, or the repository's dedicated GitHub Actions regression. It authenticates exact deck quantities, print IDs, source evolution chains, Ditto and Klefki ability wording, the advanced manual first-turn rule, and both exact-probability derivations.

**What this estimate does not measure:** actual opening success with 4 Quick Ball, 1 Ultra Ball, 1 Battle VIP Pass, Secret Box, supporter draw, Ability draw, mulligan-bonus draws, and Prize searches. It excludes opponent interaction, turn-two Stage 1 access, five Energy cards reaching discard, Electrode's self-Knock-Out Prize consequences, and Electro Rain attack permission. It cannot be interpreted as full combo setup rate, deck win rate, or a reliable assessment of the deck's tournament strength.

**Next experiment:** couple these physical base identities to a joint search/discard and draw policy, then model turn-two evolution plus the Prize-state-dependent five-Energy Bomb action without double-spending connectors.
