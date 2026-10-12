# Forest Seal Stone rescues additional dual-entry champion starts

## Result

The 2026 Aichi Shadow Rider champion list contains one Forest Seal Stone and three Shadow Rider Calyrex V. If the Stone and a V host are naturally present by the first draw going second, **Star Alchemy** can supply one more search output beyond the available Quick Ball and Mysterious Treasure cards. It can retrieve a missing Radiant Eternatus or Tapu Lele-GX from the deck, or search Hisuian Heavy Ball to recover one of these Basics if Prized.

Within the earlier, restricted **Wonder Tag entry followed by Radiant Eternatus's two-VMAX launch**, adding these Stone-specific lines increases the exact Basic-valid opening probability:

| One-card normal-search discard policy | Without Stone routes | Stone-only additional cases | Combined |
| --- | ---: | ---: | ---: |
| Only held Psychic Energy disposable | 15.085879759% | **+2.030765710 pp** | **17.116645469%** |
| Any mechanically expendable hand card | 23.314279776% | **+2.055409735 pp** | **25.369689511%** |

This extension assumes the V and Stone are **naturally available in the opening-plus-one-draw hand**, no card has yet spent the VSTAR Power, the Pokémon V can enter play and host an unsuppressed Tool, and the Bench has room. A V found by a normal search or via Fog Crystal is excluded from this Stone extension.

For a cross-check, remove the Wonder Tag requirement and retain Radiant's two-VMAX objective. The new exact totals are:

- **45.643268335527%** with Energy-only normal-search payment.
- **53.106724029444%** with unrestricted normal-search payment.

Both exactly recover the independently developed natural-V-host Forest Seal Stone numbers in [the original Stone study](../shadow_rider_forest_stone_frontier/). This verifies the distinct search channel logic against a separate implementation and physical oracle.

## Physical resource model

The prior [dual-entry kernel](../../tools/shadow_rider_dual_entry_launch.py) uses the actual 60-card champion group counts: eleven non-target Basics (three V), one Radiant, two Tapu Lele, four VMAX, four Mysterious Treasure, one Quick Ball, one Hisuian Heavy Ball, eleven Psychic Energy and 25 neutral cards (one Stone). The [Stone extension](../../tools/shadow_rider_stone_dual_entry.py) conditions on:

- Stone in the observed first eight cards: if f of the 25 other cards are observed, probability f/25.
- At least one eligible V among the o observed non-target Basics: conditional probability \`1 - C(8,o)/C(11,o)\`.
- Original seven containing an appropriate Active Basic, preserving the necessary target physical copies. If the only opening Basic is Lele, one Lele copy is assigned Active; if the only starter is Radiant, the modeled entry is impossible.
- Prize placement of Radiant, Lele, VMAX **and the singleton Heavy Ball**, so the Stone → Heavy Ball route is only counted when that actual Heavy Ball remains in the deck.

The two observability events for Stone and V are independent conditional on grouped physical-class counts because these cards belong to different classes. This allows exact reduced Fractions without introducing large redundant card categories.

For each missing trigger, the solver chooses between one normal search Item, one already-held Heavy Ball for a Prized target, the Stone's direct target search, and Stone's search for a deck-resident Heavy Ball that recovers a Prized target. It checks one use per physical resource. A single Stone can supply only one of the two triggers, which matters when both are missing. The search Items each cost one card, and the mechanical scenario explicitly reserves the Stone and needed trigger copies instead of discarding them as normal-search payment.

## Independent verification

The [Stone extension reproducer](stone_reproduce.py) enumerates physical labeled opening cards, Prizes, bonus cards and first-draw cards in two small decks with explicit Stone and V-host identities. It searches for distinct physical source assignments under both payment policies, with and without the Wonder Tag goal. All exact grouped probabilities agree with the independent physical oracles, including the disjoint original/Stone-only route partition. The published Aichi source is validated by the companion [entry reproducer](reproduce.py). CI runs both.

Run from repository root:

\`python results/shadow_rider_dual_entry_launch/stone_reproduce.py\`

## Interpretation and remaining scope

The Stone supplement provides an additional **2.03–2.06 percentage points** of this narrow early combined access objective, conditional on source-preserving actions and the listed setup assumptions. It cannot establish how many games or matches the deck will win. The Stone is a valuable once-per-game search resource whose alternative later uses are excluded, while Wonder Tag may use the one Supporter action per turn. Also excluded are Fog Crystal or paid search Items finding a V host, Item/Ability locks, effects that remove Tool effects, evolving VMAX, the downstream Supporter target, active promotion and turn-two damage.

Further work should compare the *choice to spend* Star Alchemy immediately against saving it for later in concrete two-turn branches, with a representative opponent field and a more complete card-action simulation.
