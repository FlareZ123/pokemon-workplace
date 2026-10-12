# Mega Absol / Crobat: exact first-turn Item and Ability lock lattice

## Question

The 2026 Aichi [published Mega Absol ex/Garbodor deck](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) includes Crobat V, Forest Seal Stone and Adventure Bag. The [unlocked Stone bridge](../absol_garbodor_stone_bridge/) reverses one restricted access ranking between a third-Mega cut of Temple of Sinnoh versus Crobat V. How sensitive is that reversal to an opponent's or our own locks?

Lock conditions affect *which edges actually exist* in the physical access plan. The 2025 Advanced Player's Rulebook distinguishes Item cards from Pokémon Tools even when older Tools carried the `Item` printed header. Thus a pure Item lock can block Adventure Bag, search Items and Hisuian Heavy Ball while leaving a **held Forest Seal Stone Tool attachment** available. In contrast, an Ability lock that suppresses Stone-granted **Star Alchemy** removes the VSTAR route while leaving ordinary Trainer-Item search available. A combined lock removes both channels.

## Exact access, conditional on a Basic-valid seven-card opener

Six physical Prize cards and one natural draw are jointly accounted for. All three 60-card decks have independently checked October 12, 2026 paper Expanded snapshot eligibility.

| Lock state throughout access window | Published 2 Mega | +Mega / −Temple | +Mega / −Crobat |
| --- | ---: | ---: | ---: |
| **No Item or relevant Ability lock** | 69.985333% | **76.314588%** | 75.410322% |
| **Star Alchemy blocked, Items available** | 68.319327% | 74.931248% | **75.410322%** |
| **Items blocked, held Tools and Star Alchemy available** | 34.120403% | 45.308579% | **45.798873%** |
| **Both channels blocked** | 32.519203% | 43.929817% | **45.798873%** |

The model holds all other aspects of the restricted first-turn access policy constant. Under Item lock, the counted lines are a Mega already held or a **held Crobat V plus held Forest Seal Stone** with another Mega remaining in deck. Adventure Bag cannot fetch Stone under Item lock; Hisuian Heavy Ball cannot recover a Prized Crobat; all named Item searches are unavailable. Under Ability lock, the [prior paid named-Item frontier](../absol_garbodor_named_item_frontier/) applies. Under both locks, only a directly held Mega meets this restricted endpoint.

These states intentionally isolate one lock at a time: a particular real card may block both Items and Tools, may deactivate the Pokémon carrying the lock, may have asymmetric effects, or may allow a different route. The table does not claim a general lock-deck matchup forecast.

## Exact mixture break-even analysis

Consider an artificial population in which the encounter is *unlocked* with probability `1 − p`, and in one particular locked state with probability `p`. Under this one-event objective, the +Mega/−Temple variant is initially ahead of the +Mega/−Crobat variant by **0.904266 percentage points**. Its ranking changes once the modeled lock prevalence crosses:

| Locked state substituted for unlocked | Break-even `p` |
| --- | ---: |
| Star Alchemy blocked only | **65.368294%** |
| Items blocked only | **64.842422%** |
| Both channels blocked | **32.605880%** |

This is simple exact rational interpolation of the [underlying physical access probabilities](../absol_garbodor_stone_bridge/) and **does not predict actual metagame shares, decision timing, match-win probabilities, or how the Temple loss affects the opponent**. For example, a game facing Item lock only after the normal first-turn access window belongs to the unlocked scenario for this experiment.

## Method and validation

The solver `tools/mega_absol_stone_bridge.py` enumerates hands, one natural draw, and the *joint* Prizing of Mega, Crobat and Stone with exact integer coefficients. The results include the separate three additional lock-state flags. `results/absol_garbodor_stone_bridge/reproduce.py` verifies each flag against an **independent exhaustive labeled hand/Prize/draw oracle** in three 12-card toy decks, checks the card text, validates the full published and two counterfactual 60s, and calculates the three break-even weights with exact `Fraction` arithmetic.

Reproduce: `python -m results.absol_garbodor_stone_bridge.reproduce`. **[Windows CI run 38278438352](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278438352) passed**, independently supported by [run 38278381413](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278381413), including the earlier named-Item and Dark Asset regression suites. The restricted Dark Asset line remains separately tested in [its companion study](../absol_garbodor_darkasset_frontier/).

## Strategic implication

The apparent ranking of even a single deck-slot change depends on the action-resource constraints assumed for the opening. Crobat V's Tool-host value can be unusually important when both the relevant Tool and Crobat are already in hand under pure Item lock; it contributes nothing to the first-turn Stone route when Star Alchemy is suppressed. The Temple cut simultaneously weakens Special Energy disruption, which this entire calculation omits.

Before recommending a tournament swap, measure realistic setup policies against representative Item locks, Ability locks, Tool locks and the lock-establishment turns, then estimate complete games. This table is a reproducible stress test of an access proxy, not a definitive deck optimization.
