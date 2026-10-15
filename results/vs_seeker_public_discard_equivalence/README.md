# VS Seeker: public-discard historical action equivalence

## Question

Does the historical VS Seeker's explicit `Search your discard pile ... show it` provide a different legal choice or opponent observation than the XY-era `Put a Supporter card from your discard pile into your hand` wording?

Two archival sources, **EX Deoxys `ex6-100`** and **Platinum Rising Rivals `pl3-140`**, use the first text. Expanded-range sources **XY Phantom Forces `xy4-109`** and **XY Roaring Skies `xy6-110`** use the second. All four source records identify them as Trainer Items.

## Model and result

A public discard has distinguishable physical card instances. Both effects allow choosing exactly one Supporter in that pile, moving that physical instance to the hand while keeping the deck unchanged, and disclose the retrieved card's identity to the opponent. In the older wording this observation is explicit; the XY wording moves an identifiable face-up card out of a public zone. If no Supporter is available, neither Item changes the game state or has a legal useful action.

The executable test enumerates all ordered discard piles of length 0–6 from two Supporter types and two ineligible types, including duplicate type copies, with three hand variants and two deck variants. It compares the chosen instance, hand/discard/deck material changes, opponent's public observation, and availability for every state.

This is a bounded exhaustive *model* of the relevant transfer and public information. An arbitrary-size extension follows by the same one-card deletion/insertion bijection for each eligible physical Supporter, assuming the discard is fully public. It does not simulate opponents, match win rates, or chain-specific card effect semantics.

## Reproduce

Run `python -m results.vs_seeker_public_discard_equivalence.reproduce`. The test checks exact four-print card text and calls `tools/vs_seeker_public_discard_equivalence.py`. The Windows workflow `.github/workflows/validate-vs-seeker-public-discard.yml` runs the regression.

**Tournament printing policy remains unresolved for pre-Black & White physical prints.** This analysis establishes action/observation agreement in the modeled public-discard state, and does not independently certify EX Deoxys or Platinum VS Seeker prints as presently admissible for paper Expanded. Distinguish it from the legality of the XY print used as the target.
