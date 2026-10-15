# Mega Absol ex / Garbodor with Lumineon V (experimental 60)

**Evidence status:** A one-card paper Expanded counterfactual derived from Yusuke Kobayashi's eighth-place Aichi Open League list, 10 May 2026. This variant was not the published tournament list and has no observed match-win evidence.

**Exact change:** swap one `swsh3-104` Crobat V for one `swsh9-40` Lumineon V. Keep the two Mega Absol ex, one Tapu Lele-GX, Forest Seal Stone, Adventure Bag, both Temple of Sinnoh, all eight printed Supporters, seven Energy and all other 59 physical cards unchanged.

**Full human-playable 60:** Copy the complete published table from [Mega Absol ex / Garbodor](../mega-absol-garbodor/) and replace its single Crobat V row with **1 Lumineon V (`swsh9-40`)**. The complete independent 60-card [print-level JSON manifest](deck.json) explicitly lists every card and copy count. The reproducer verifies that the proposed list differs in exactly this one slot and passes the repository's October 15, 2026 paper Expanded snapshot construction test.

## Why this particular swap?

Tapu Lele-GX's **Wonder Tag** and Lumineon V's **Luminous Sign** each search for a Supporter when the Pokémon is played **from hand onto the Bench**. A held first-turn Supporter is already usable without either tutor; including both effects can overstate their additional value. This analysis therefore evaluates the union of the eight actual Supporter cards printed in the published list.

Crobat V's **Dark Asset** instead draws until the hand has six cards when played from hand to Bench. It can find arbitrary missing cards and discard payments, making the original tournament slot strategically valuable even when a Supporter is already available. The exchange is not a confirmed competitive improvement.

Lumineon is also a Pokémon V and therefore remains a host for the deck's existing Forest Seal Stone **Star Alchemy**. Both lines occupy a vulnerable two-Prize Bench slot and share active Ability-lock problems under Garbotoxin. The existing [single-Crispin](../../absol_lumineon_supporter_frontier/) and [Crispin-plus-Stone](../../absol_lumineon_stone_overlap/) studies cover different, narrower material endpoints.

## Restricted access study

See [the eight-Supporter physical experiment](../../tests/absol_lumineon_any_supporter/) for the precise assumptions and reproduced results. Its success condition is having **any** of the eight named Supporter cards in hand by the first natural draw or one payable Basic-tutor Item followed by a hand-to-Bench Tutor Ability. It accounts for a seven-card Basic-valid hand, six Prizes, start-Active constraint, search target Prizing, Quick/Ultra Ball Energy-only discards, Pokémon Communication's spare Pokémon, and Hisuian Heavy Ball. Battle VIP Pass directly placing a tutor from deck does not trigger Wonder Tag or Luminous Sign.

This is an opening material-access model with a selected line of play, no opponent, no later turn, no Ability-lock timing, no Crobat draw and no actual matchup win rate. The source Aichi eighth-place 60 remains the stronger supported tournament starting point.
