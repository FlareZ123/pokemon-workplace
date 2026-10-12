# Wobbuffet Bide Barricade is asymmetric against Aichi champion Shadow Rider

## Question and factual inputs

The 2026 CL Aichi Open League 10th-place [Haruku Yoshioka Regidrago](../regidrago_aichi_top10_playable/) plays one Wobbuffet (Phantom Forces, `xy4-36`). Its **Bide Barricade** Ability only functions while Wobbuffet is Active and suppresses Abilities on **non-Psychic Pokémon** in play, in hands and in discard piles, on *both* players' sides.

The champion [Yasunori Kato Shadow Rider list](../regidrago_shadow_rider_temporal_counterplay/) is centered on Psychic VMAX's Underworld Door. The printed Wobbuffet exception preserves that Ability, regardless of Wobbuffet's lock being active, unless some different lock independently suppresses it.

This study uses the two real, validated 60-card manifests and the bundled full English card snapshot. It audits **every ability-bearing Pokémon entry**, not only the central attackers, and weights the inventory by actual deck copies.

## Exact static full-deck Ability inventory

| Hypothetical owner under Regidrago's Active Wobbuffet | Copies with printed Abilities | Ability copies suppressed for non-Psychic typing | Ability copies exempt as Psychic |
| --- | ---: | ---: | ---: |
| Yoshioka Regidrago owner | **11** | **7** | **4** |
| Opposing Kato Shadow Rider champion | **11** | **1** | **10** |

In the Regidrago list the seven potentially suppressed copies are three **Regidrago VSTAR Legacy Star**, one **Kyurem Plasma Bane**, one **Hisuian Goodra VSTAR Moisture Star**, one **Dedenne-GX Dedechange**, and one **Squawkabilly ex Squawk and Seize**. Its four Psychic exceptions are **Tapu Lele-GX Wonder Tag**, **Latias ex Skyliner**, **Marshadow Resetting Hole**, and Wobbuffet's own **Bide Barricade**.

In the Shadow Rider champion list, ten Psychic copies with Abilities are exempt: four **Shadow Rider Calyrex VMAX Underworld Door**, two **Lillie's Clefairy ex Fairy Zone**, two **Tapu Lele-GX Wonder Tag**, one **Latias ex Skyliner**, and one **Marshadow Resetting Hole**. The **one Radiant Eternatus** has Dragon typing and **Climactic Gate**, so its Ability may be suppressed when the effect applies.

This is a **static count of potential card-specific Ability text occurrences across complete decks**. Only in-play Pokémon can perform in-play Abilities; some Abilities apply only on Bench entry, while others can be used only in a specific zone. Copy totals are not a statement that all 22 Pokémon are simultaneously present or that each can use its Ability at the same time. Timing, actual zones, existing KO/Prize state, and other Ability locks all matter.

The count demonstrates an unusually asymmetric counter-ability profile in this named matchup. Merely calling Wobbuffet an Ability-lock Pokémon would obscure the Psychic typing of Shadow Rider's draw engine and the self-suppression of Regidrago's non-Psychic acceleration/draw sources.

## Board-level consequence

Assume Active Wobbuffet, active effect of Bide Barricade, and no other Ability locks:

- A Shadow Rider Calyrex VMAX on the opponent's Bench still has **Underworld Door**, can attach Psychic from hand to a *Benched* Psychic Pokémon and draw two, subject to that Ability's ordinary timing.
- Regidrago VSTAR's **Legacy Star** cannot function while the Wobbuffet lock is applied to it; if Wobbuffet retreats to the Bench, the Active-dependent lock ceases, and Legacy Star is potentially available if unused.
- Latias ex's Psychic-type **Skyliner** remains operational on the Regidrago side. Basic Wobbuffet therefore has no Retreat Cost, enabling a normal once-per-turn zero-Energy retreat when a Benched replacement exists and other restrictions do not prevent retreat. The same Latias ex effect cannot give evolved Regidrago VSTAR free retreat.
- Suppression applies to matching non-Psychic Pokémon in hand too, so hand-triggered Squawkabilly ex and Dedenne-GX Abilities cannot be assumed accessible while the Wobbuffet is actively suppressing them.

The blanket suppression effect concerns Ability availability, without directly negating Pokémon attacks. A separate approach is needed to model lock start/end, actual zones, concurrent locks and access to promotion.

## Reproduction

The [single-file regression](reproduce.py) loads both 60-card tournament manifests and the source card snapshot. It independently recomputes exact copy counts, types and active Wobbuffet's printed text, asserts the 7/4 and 1/10 partitions, and checks the named Ability owners' types. Reprints and other archetypes are not represented by the two tournament manifests.

For other opponents, Wobbuffet may suppress substantially more of the opposing setup engine. This study is deliberately matchup-specific and cannot establish optimal Regidrago play, win probabilities or Wobbuffet's marginal deck-slot value.
