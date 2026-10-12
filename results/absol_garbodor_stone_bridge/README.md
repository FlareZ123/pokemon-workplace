# Crobat V / Forest Seal Stone reverses a Mega Absol first-turn access ranking

## Question and exact-print source

The published [May 10, 2026 Aichi Open League eighth-place Mega Absol ex/Garbodor deck](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) contains exactly one **Crobat V** (`swsh3-104`), one **Forest Seal Stone** (`swsh12-156`), and one **Adventure Bag** (`sm8-167`). Crobat V is the *only* Pokémon V in that deck. The original [named-Item comparison](../absol_garbodor_named_item_frontier/) found a small first-turn Mega-access advantage for +1 Mega Absol / −1 Crobat over +1 Mega / −1 Temple of Sinnoh. That comparison excluded the Crobat-only VSTAR Power route.

Card text establishes:

- Forest Seal Stone can grant **Star Alchemy** to a Pokémon V with the Tool attached, searching for *any one card* in the deck, subject to the once-per-game VSTAR Power rule.
- Adventure Bag searches the deck for up to two Pokémon Tools, including Forest Seal Stone.
- Hisuian Heavy Ball can exchange itself for a Basic Pokémon in the six Prize cards, including a Prized Crobat V.
- Crobat V's **Dark Asset** can draw cards when played onto the Bench from hand, a *different* benefit that this model intentionally does not evaluate.

The three complete source-print 60-card versions retain their existing [deck legality proofs](../absol_garbodor_named_item_frontier/) and are re-adjudicated in this study.

## Exact conditional first-turn results

The event is **obtaining a Mega Absol ex by the first natural draw plus one of the declared immediate sources**. The player has a valid seven-card Basic starting hand, sets six physical hidden Prize cards, and takes one natural draw. A Mega may already be held, be obtained by one individually payable named Item, or be fetched from the deck with a Forest Seal Stone attached to Crobat V.

| Physical event | Published 2 Mega | +Mega / −Temple | +Mega / −Crobat |
| --- | ---: | ---: | ---: |
| Prior named-Item paid access, excluding Stone | 68.319327% | 74.931248% | 75.410322% |
| Crobat held, Stone route feasible | 3.509105% | 3.484634% | 0% |
| Crobat Prized, Heavy Ball recovery and Stone route feasible | 0.231825% | 0.246857% | 0% |
| **Union: named-Item or Stone access** | **69.985333%** | **76.314588%** | **75.410322%** |
| **Marginal Stone gain over named-Item baseline** | **+1.666006 pp** | **+1.383340 pp** | **0 pp** |
| Crobat physically held by first draw | 17.326491% | 16.607538% | 0% |

The two raw Stone-route rows include worlds in which an existing named-Item route already gets Mega, so their sum is **not** the marginal improvement. The union explicitly prevents double credit.

The original comparison favored cutting Crobat by **0.479074 percentage points**. With the Crobat-only Tool path available, preserving Crobat and cutting Temple leads by **0.904266 points** under this *same restricted access objective*. This is a genuine narrow ranking reversal.

## Execution contract

The earlier named-Item route is unchanged: first-turn Battle VIP Pass; Hisuian Heavy Ball for a **Prized Mega**; Quick Ball with one held Energy discard; Ultra Ball with two held Energy discards; or Pokémon Communication with a spare held Pokémon after reserving one opening Basic as Active. A directly held Mega always qualifies. No extra searches or draw effects are assumed.

A separate Stone route succeeds if:

1. A Mega Absol remains in the draw deck (and is neither held nor Prized).
2. Forest Seal Stone is physically held, or Adventure Bag is held with Forest Seal Stone **unprized and still in the deck**.
3. Crobat V is physically held by the first draw, or Crobat V is Prized and a physically held Hisuian Heavy Ball can retrieve it.
4. A Bench or Active placement and a Tool attachment are available, the VSTAR Power is unused, and no effect blocks Items or Abilities as relevant.

There is no simultaneous double spending: the union represents a choice of one valid route. If a Quick Ball, Ultra Ball or Pokémon Communication can search Crobat while Mega remains in deck, that same named Item can search Mega directly under the *same payment*, so this Crobat-finding detour offers no additional target access under the declared one-step objective. The model instead counts genuinely new Crobat-held or Crobat-from-Prizes paths.

**Important lock interaction:** If Garbodor's own Garbotoxin is already suppressing Abilities, using the Stone-granted VSTAR Power can be blocked. The model explicitly assumes Abilities are available when its Stone route executes. It does not claim that the route remains live during an established Garbotoxin lock, an opposing Ability lock, or Item lock.

## Mathematical method and reproducibility

`tools/mega_absol_stone_bridge.py` refines the previous ten-category multivariate hypergeometric solver by separating Crobat V, Forest Seal Stone and Adventure Bag as distinct physical categories. For each Basic-valid opening and one natural draw, it integrates the *joint* Prize counts of Mega Absol, Crobat V and Forest Seal Stone, keeping all other Prizes in a residual category. Every mass uses exact integer products of binomial coefficients and `Fraction` normalization.

`results/absol_garbodor_stone_bridge/reproduce.py` also independently enumerates all labeled physical starting hands, disjoint Prize packets and legal first natural draws on three 12-card toy decks. This oracle does not rely on the category-weighted or Prize-hypergeometric enumeration. The seven exact event ratios agree in every toy case, including the Crobat-free counterfactual. It then verifies the actual card text and each full 60-card deck's October 12 paper Expanded snapshot eligibility.

Reproduce on Windows or in CI with `python -m results.absol_garbodor_stone_bridge.reproduce`.

## Limitations and next research

This is an **exact probability for a deliberately restricted material-access problem**, with **no measured win rate**. It omits Crobat's Dark Asset hand-size-dependent draw, Squawkabilly and Dedenne draws, Supporter draw, recursive Item chains, search contention beyond the modeled single route, Tool displacement, already-used VSTAR Powers, opponent interference, Garbotoxin timing and actual game-turn policies. The Energy-only discard rule is a test policy, not a claim of optimal real play. Temple of Sinnoh's actual Special Energy disruption value is also outside the objective.

Next priority: include the **Dark Asset** draw and actual first-turn sequencing, while explicitly modeling the choice between establishing Garbotoxin and using Star Alchemy. Those benefits and liabilities may change the deck ranking again. Until match testing, the published tournament deck remains the evidence-backed reference.
