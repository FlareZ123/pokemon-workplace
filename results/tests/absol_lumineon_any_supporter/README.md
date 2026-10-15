# When Mega Absol already holds any of eight Supporters, how valuable is Lumineon V?

**Research class:** exact conditional first-turn material access. **Date:** 15 October 2026. **Source:** the published [Aichi eighth-place Mega Absol/Garbodor deck](../../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json), versus the [complete one-slot Lumineon V counterfactual](../../decks/mega-absol-lumineon-support-tutor/). **Competitive wins:** unmeasured.

## Question

Prior repository experiments [tested access to singleton Crispin](../../absol_lumineon_supporter_frontier/) and [deducted shared Forest Seal Stone access](../../absol_lumineon_stone_overlap/). Here we ask a different question: if **any of the eight actual Supporter copies** qualifies, what is the additional probability of possessing at least one Supporter after replacing Crobat V with Lumineon V? Already held Supporters count as success, so a redundant Supporter-search ability receives no extra reward in those worlds.

Both 60s retain 2 Mega Absol, 1 Tapu Lele-GX with Wonder Tag, 8 singleton Supporters, 4 Quick Ball, 2 Ultra Ball, 1 Pokémon Communication, 1 Hisuian Heavy Ball, 7 Energy, 2 Temple of Sinnoh, 1 Forest Seal Stone, and 1 Adventure Bag. The published one has Crobat V; the counterfactual has Lumineon V in that slot. Both have 10 Basic Pokémon for valid opening conditioning.

## Exact access results

Conditional on a Basic-valid first 7, 6 hidden Prizes, and one natural draw:

| Restricted event | Published Crobat V | Lumineon V swap | Increment |
| --- | ---: | ---: | ---: |
| Any of eight Supporters already held | 68.327837% | 68.327837% | 0 |
| Hand-to-Bench Supporter tutor accessible through one permitted route | 38.063150% | 49.710173% | +11.647023 pp |
| New Supporter fetchable when none is held | 14.689987% | 18.687926% | +3.997939 pp |
| **Held or fetchable Supporter (union)** | **83.017823%** | **87.015762%** | **+3.997939 pp** |

The distinction between 11.6470 pp *raw tutor access* and 3.9979 pp *incremental all-Supporter possession* is the material finding. The source line contains eight alternative Supporters already, and the physical first-hand union is large. About 34.33% of the raw tutor-access probability uplift survives as new all-Supporter possession under this deliberately coarse endpoint. A singleton-specific Supporter endpoint can exhibit a very different substitution value.

## Provenance and model

- [Exact multivariate hypergeometric solver](../../../tools/absol_support_tutor_frontier.py) enumerates the complete 60-card role partition, opening hand, first draw, and *joint* six-Prize counts of tutors and Supporters, accumulating integer masses into rational `Fraction` results. Both candidate 60s are fully materialized.
- [Independent reproducibility test](reproduce.py) enumerates physically labeled hand, Prize packet, and first-draw worlds in three 11- or 12-card toy cases and asserts every event ratio exactly matches the multivariate implementation. It separately checks both complete 60-card paper Expanded construction and print eligibility for 15 October 2026.
- Card roles are checked against source print text: Tapu Lele-GX **Wonder Tag** and Lumineon V **Luminous Sign** trigger only when played from the *hand* onto Bench; Crobat V has the different **Dark Asset** draw effect. Search-Item feasibility is constrained by physical held cards.

One route may be used in a hypothetical immediate sequence: directly held benchable tutor; one payable Quick Ball (discard at least one held Energy); one payable Ultra Ball (two held Energy); one Pokémon Communication (second Pokémon after choosing initial Active); or one Hisuian Heavy Ball (tutor actually Prized). The tutor must have a legal hand-to-Bench entry; the searched Supporter must still be in deck. Battle VIP Pass puts Basic Pokémon directly from deck onto Bench and is therefore excluded as a Wonder Tag/Luminous Sign activation route.

## Strategic interpretation and exclusions

This establishes a restricted probability advantage for Lumineon **if the game only cares about locating any Supporter**. Real play values named Supporter function differently; holding Roxanne, Karen or Iono is not interchangeable with needing Crispin or Guzma on a particular turn. A Supporter may also be unusable or dominated by a different Supporter action.

This model **does not credit Crobat V's Dark Asset** (the source deck's separate exact restricted positive-Dark-Asset access is [35.280897%](../../absol_garbodor_darkasset_frontier/)). Neither does it integrate the shared Forest Seal Stone Star Alchemy, which could further reduce Lumineon's access premium, or the draw/storage implications of Secret Box, early Garbotoxin suppression, Bench occupancy, opponent locks, Prize pacing, multi-turn setup and match wins. The [previous Stone-overlap analysis](../../absol_lumineon_stone_overlap/) demonstrates that this overlap can be material for the distinct singleton-Crispin endpoint. Thus, **do not rank the Lumineon variant above the eighth-place published Crobat deck based on this proxy**.

## Replication

The source code is at `tools/absol_support_tutor_frontier.py`; the runnable Python module is `results.tests.absol_lumineon_any_supporter.reproduce`. Manual Windows validation is attached to `.github/workflows/validate-agent1-stone-bridge.yml`, which re-runs the existing related exact models and this new study.
