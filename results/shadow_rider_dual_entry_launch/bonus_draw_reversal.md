# Mulligan bonus-card paradox: acquiring a card can remove a required VMAX target

## Finding

In the actual 2026 Aichi champion Shadow Rider list, adding one voluntary bonus card after an opponent mulligan improves the average probability of assembling a Radiant Eternatus + Tapu Lele-GX hand-to-Bench entry line. A **small subset of previously successful configurations becomes unsuccessful**, however, because drawing a Shadow Rider Calyrex VMAX out of the deck can leave only one VMAX there for Radiant's Climactic Gate.

The exact first-extra-bonus-card transition, coupled on the same opening seven, Prizes, first deck card, and second deck card, is:

| Search-payment policy | Forest Seal Stone considered? | Prior joint access | Newly rescued outcomes | Previously feasible outcomes lost | New joint access |
| --- | :---: | ---: | ---: | ---: | ---: |
| Psychic Energy only | No | 15.085879759% | +5.135391183 pp | −0.097693288 pp | 20.123577653% |
| Mechanically expendable cards | No | 23.314279776% | +4.972610391 pp | −0.165883651 pp | 28.121006516% |
| Psychic Energy only | Yes, naturally held V + Stone | 17.116645469% | +5.760239076 pp | −0.111282860 pp | 22.765601685% |
| Mechanically expendable cards | Yes, naturally held V + Stone | 25.369689511% | +5.480302230 pp | −0.180287763 pp | 30.669703979% |

For this specific objective, the first bonus card is still **beneficial on average**. The losses matter because they expose a counterexample to the assumption that a larger hand always weakly improves the probability of every deck-search-based endpoint.

## Why the exact loss has a simple formula

Let A_m denote an executable restricted dual entry line after m bonus cards and the one natural going-second first-turn draw. Let V_m be the number of Shadow Rider Calyrex VMAX remaining in the searchable deck in that same coupled state.

Between m and m+1 draws, already accessible hand cards, Item search sources, discard payments and Stone hosts remain available or become more available under this restricted action contract. Drawing a missing Radiant, Lele or Heavy Ball directly into the hand can substitute for a search. The only way a previously successful dual-entry state fails when one more card is drawn is if:

1. A_m was true;
2. exactly **two** VMAX still remained in the deck after the previous sample;
3. the additional drawn physical card is one of those two VMAX.

Thus the exact backward transition is

\`P(A_m and not A_{m+1}) = P(A_m and V_m = 2) * 2 / (N-H-P-1-m)\`.

The result \`P(A_m and V_m=2)\` is obtained without approximate independence:

\`P(A_m with V_m >= 2) - P(A_m with V_m >= 3)\`.

Both probabilities are computed by reusing the full exact physical-class solver, changing only the minimum searchable VMAX threshold. Subtracting the two exact fractions isolates the states with precisely two eligible targets in the deck. At the champion's first bonus decision, 46 cards are still in the draw deck after the initial seven, six Prizes and first natural draw.

If \`p_m=P(A_m)\`, the forward newly rescued probability follows exactly from conservation:

\`P(not A_m and A_{m+1}) = (p_{m+1}-p_m) + P(A_m and not A_{m+1})\`.

The independently tested [kernel](../../tools/shadow_rider_bonus_vmax_competition.py) uses these two identities with exact Python Fraction arithmetic, without Monte Carlo.

## Independent labeled-card verification

The [reproducer](bonus_reproduce.py) performs a separate physical enumeration for two reduced decks. Each world specifies an **ordered first and second deck card** after the same original legal opening and Prize selection, with the starting Active chosen from the opening before either card is seen. It checks physical Item/Stone/Heavy Ball one-use source allocation, exact target presence, VMAX count in the deck, and payments. That fully independent paired oracle reproduces all four exact probabilities (before, newly rescued, lost, after), for both Energy-only and unrestricted payments, and both with and without naturally available Stone and V host.

It also checks the real 60-card benchmark percentages. The shared [CI validation](../../.github/workflows/validate-shadow-rider-dual-entry-launch.yml) runs the reproducer along with the other two independent dual-entry test suites.

## Competitive interpretation

A player **may decline** drawing some optional cards granted by opponent mulligans. If their specific Radiant/VMAX line is already assembled and only two targets remain searchable, an extra card has a small chance to disrupt that line by drawing away a VMAX, while potentially helping other plans. Whether to take the card is an information-dependent decision, not a universal instruction to skip mulligan bonuses.

The computed 0.10–0.18-percentage-point loss rates are *unconditional* over Basic-valid opening states, not the conditional loss risk in a known near-complete hand. They also assume one first-turn natural draw and the stated limited source routes, with no late-stage reshuffle, evolution of held VMAX, alternative placement from hand, return-to-deck effect, lock interactions or strategic value for the extra card. These probabilities do not measure real match-winning chances.

The same phenomenon should appear whenever a search-based endpoint requires a minimum stock remaining in the deck, including multi-target direct-to-Bench effects. A next step is a state-conditional bonus draw decision rule using the observed opening's target stock estimate, rather than a single unconditional success probability.
