# The shared Forest Seal Stone route and eight-Supporter tutor redundancy

**Evidence class:** exact conditional first-turn resource-access frontier and source-verified legal 60-card deck swap, with physically labeled toy regression. **Format:** paper Expanded, Black & White onward, legality snapshot 15 October 2026. **Status:** model code and reproducibility check at [reproduce.py](reproduce.py).

## Research question and existing evidence

The original 2026 Aichi eighth-place [Mega Absol/Garbodor deck](../../decks/mega-absol-garbodor/) contains Crobat V, Tapu Lele-GX, Forest Seal Stone and eight different Supporters. The [experimental standalone Lumineon V variant](../../decks/mega-absol-lumineon-support-tutor/) replaces Crobat in exactly one slot. Our [previous any-Supporter study](../absol_lumineon_any_supporter/) showed that Lumineon makes a hand-to-Bench Supporter-search body more accessible, but that much of this does not improve possession of **any** Supporter because eight alternatives can already be held.

Forest Seal Stone adds a second form of redundancy. A host Pokémon V can use the **Star Alchemy** VSTAR Power granted by the Stone to search *any* card, including a Supporter. The Crobat and Lumineon variants both have exactly one Pokémon V host, so both can use this source. This model measures the union of: a held Supporter; a legal Tapu Lele Wonder Tag / Lumineon Luminous Sign line; and a Forest Seal Stone Star Alchemy line.

## Physical assumptions

The denominators condition on a Basic-valid seven-card opening hand, six random physical Prizes, and the first natural draw. Roles are tracked separately for Lele, the single Pokémon V host, all eight Supporters, Forest Seal Stone, Adventure Bag, Mega Absol, other Basics, evolutions and named search Items.

One independently payable named Item can be used within a route. Quick Ball needs a held Energy card to discard; Ultra Ball needs two. Pokémon Communication needs a physically spare Pokémon after starting Active is committed. Hisuian Heavy Ball can retrieve a Prized Pokémon V or Basic tutor. Adventure Bag may obtain an in-deck Stone only when the host is already in hand; combining Bag and a second Pokémon-search Item is outside the allowed one-Item budget. Attaching an already held Stone to a host and using Star Alchemy does not require that host to have entered the Bench from hand; an Active Pokémon V also qualifies.

All of these are **material feasibility events** integrated over physical hidden zones. The solver knows which cards are Prized to calculate the *outcome* of hypothetical access paths; it does not establish a legitimate K0 player policy that knows those Prize identities.

## Independent verification

[The exact rational solver](../../../tools/absol_any_supporter_stone.py) uses an explicit 14-category joint physical partition and multivariate hypergeometric combinatorics. [The reproducer](reproduce.py) independently enumerates every individually labeled opening, Prize packet, and first draw in three tiny decks for both Crobat and Lumineon policies. It verifies all event fractions against the solver and checks that the new model projected onto the previous Tutor-only 11-category solver gives **exactly the same non-Stone all-Supporter event**. The complete source and variant 60s each undergo an October 15 paper Expanded eligibility proof and exact relevant ability/tool text checks.

## Interpretation and limitations

This calculation tests **incremental search access** under explicit resource constraints. It does not test the utility of the particular Supporter reached. For example, a held Roxanne cannot simply substitute for a needed Crispin, and a turn might require other missing resources ahead of its Supporter. The model excludes Crobat's Dark Asset draws, opponents, lock effects, Supporter opportunity cost, VSTAR Power use on another strategic target, multi-Item chains, multi-turn play and real match-win observations.

A higher conditional material-access rate is therefore insufficient to recommend replacing the eighth-place published Crobat V without play-policy or matchup evidence. The companion [singleton-Crispin Stone-overlap study](../../absol_lumineon_stone_overlap/) makes a different, stricter target claim and is not interchangeable with the all-eight-Supporter event here.
