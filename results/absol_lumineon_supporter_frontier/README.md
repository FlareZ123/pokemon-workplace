# Does Lumineon V improve Aichi Mega Absol's first-turn Supporter access?

## Actual source deck and legal counterfactuals

The [May 10, 2026 Aichi eighth-place Mega Absol ex/Garbodor 60](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) contains one Tapu Lele-GX `sm2-60` and one Crobat V `swsh3-104`. Both printed Basics have hand-to-Bench abilities, but only **Tapu Lele-GX's Wonder Tag** directly finds a Supporter. The legal one-copy substitute **Lumineon V `swsh9-40`** has *Luminous Sign*, with the same Supporter search payload on hand-to-Bench entry. Since Lumineon is a Pokémon V, it preserves the deck's one host for Forest Seal Stone Star Alchemy, although it gives up Crobat's Dark Asset draw.

The complete 60-card compared cases are:
1. Published 2 Mega Absol ex / 2 Temple of Sinnoh / 1 Crobat V.
2. +1 Mega Absol ex / −1 Temple of Sinnoh, keeping Crobat V.
3. Case 2 with Crobat V replaced by Lumineon V, keeping exactly one Pokémon V.

Each is independently checked against the 2026-10-12 paper Expanded deck validator and all printed roles. The source file remains unmodified.

## Narrow exact probability: singleton Crispin in hand by first draw or one search-body route

The conditional world has one Basic-valid seven-card opening, an Active Basic chosen from that opening, six physical hidden Prizes, and the first natural draw. The named target is **Crispin**, a one-copy Supporter present in all three lists. We ask if Crispin is already in hand or could be fetched into hand by a **single legal Wonder Tag / Luminous Sign hand-to-Bench entry**, with one individually payable named Item allowed beforehand.

| Material-access event | Published Crobat | +Mega / −Temple, Crobat | +Mega / −Temple, Lumineon |
| --- | ---: | ---: | ---: |
| Crispin physically held by first draw | 12.534702% | 12.598308% | 12.598308% |
| Supporter-search Pokémon directly held and legally benchable | 9.282334% | 9.413183% | 17.349271% |
| Quick / Ultra / Communication payable bridge into a search Pokémon | 19.873763% | 20.405680% | 25.869346% |
| Heavy Ball recovering a Prized search Pokémon | 0.970841% | 0.983808% | 1.885517% |
| **Union: named singleton Supporter possession** | **42.661639%** | **43.400979%** | **52.536630%** |

The published deck has ten eligible Basic starters; replacing a Temple with a third Basic Mega Absol creates eleven. This alters the valid-opening conditioning and the first column's access probabilities. The two third-Mega cases retain identical role counts in this target model, allowing the Lumineon-versus-Crobat effect to be isolated. The source-route rows overlap, so their probabilities must not be added. The last line counts a target already in hand as success.

Under this **Supporter-specific material-access proxy**, the Lumineon substitution adds **9.135651 percentage points** over the Crobat version of the +Mega/−Temple list. This is a genuine incremental result after accounting for the printed **Tapu Lele-GX Wonder Tag** alternative. It is not an estimate of game wins, and it excludes generic Crobat card draws and Forest Seal Stone's independent ability to fetch any one card, both of which may narrow or reverse the practical difference.

## Mechanics and costs included

- Starting Active must be a Basic from the seven-card opener. Tapu Lele or Lumineon forced Active cannot later trigger its **from-hand-onto-Bench** Ability merely by occupying the Active Spot. A copy naturally drawn can be benched normally.
- One named **Quick Ball** can fetch an unprized in-deck search Pokémon into the hand after discarding a physically held Energy; **Ultra Ball** requires two held Energy. Energy-only payments are a declared hypothetical preservation policy.
- **Pokémon Communication** needs an actual second Pokémon remaining in hand after the original opening Basic was committed Active.
- **Hisuian Heavy Ball** can exchange for a Prized Basic search Pokémon, which then enters hand and can be legally played onto Bench.
- A **Battle VIP Pass** directly placing Tapu Lele or Lumineon onto Bench does not trigger its hand-entry Ability and is therefore intentionally excluded as a Supporter acquisition route.
- Crispin must remain in the deck for Ability search, unless it is already held. A Prized singleton Crispin cannot be obtained through the enumerated Ability.
- A source must be available and its Ability must be active. No Supporter contention is credited because the endpoint is **possession, before deciding whether the Supporter can be played**.

## Exact solver and independent verification

`tools/mega_absol_lumineon_supporter.py` builds a 12-category physical partition of the **complete 60-card source lists**, with distinct roles for Crispin, Tapu Lele-GX, the one Pokémon V host, Mega Absol, other Basic Pokémon, evolution cards, and Quick/Ultra/Communication/Heavy search and Energy. It enumerates all multivariate opening and one-draw states with exact combinatorial integer weights, and jointly integrates the six-Prize counts of Crispin, Tapu Lele and the host. The final ratios use Python `Fraction`.

`results/absol_lumineon_supporter_frontier/reproduce.py` independently enumerates **every physically labeled opening, Prize packet and later draw** on three twelve-card toy decks under both the Crobat and Lumineon policies, giving six exhaustive oracle comparisons. The reproducer separately verifies source card hand-to-Bench text and all three complete 60-card eligibility proofs.

Reproduce on Windows via `python -m results.absol_lumineon_supporter_frontier.reproduce`.

## Interpretation and next experiment

Crobat and Lumineon are mechanically distinct engines occupying the same valuable Basic/V-host slot. Lumineon provides another targeted Supporter search entry in a deck that already uses Tapu Lele. Crobat draws up to six based on the hand state, potentially finding many categories of cards and generating discard options, while Lumineon occupies another Bench space for a two-Prize target. The VSTAR Tool route, Garbotoxin self-lock, existing hand/search choices, exact Supporter opportunity cost, Prize plan and opponent locks can all dominate the displayed conditional proxy.

A strong next step is to extend this exact calculation with the shared Forest Seal Stone access line and **search-connector contention**, then test actual game-action policies and opponents. The published Aichi deck remains the sole demonstrated tournament baseline; the variants are legitimate research hypotheses.
