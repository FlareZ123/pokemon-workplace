# Beheeyem's self-vacating Item lock: exact blind-draw handoff baseline

## Question

How rare is a **turn-two, unassisted** Beheeyem \`Mysterious Noise\` lock handoff when a replacement Active Pokémon must already be evolved and ready to take the Active Spot? This experiment separates mechanical reachability from practical AMR without pretending to simulate an optimized search engine.

Source cards in the bundled paper Expanded pool:

- Beheeyem \`sm11-91\`: \`Mysterious Noise\` costs three Colorless Energy, does 90 damage, shuffles Beheeyem and attached cards into the deck, and stops the opponent playing Items from hand during their next turn.
- Triple Acceleration Energy \`sm10-190\`: provides three Colorless Energy when attached to an Evolution Pokémon. Because Beheeyem shuffles itself and attached cards back into the deck during the attack, it is no longer attached when its end-of-turn discard condition would otherwise matter.
- Honchkrow-GX \`sm10-109\`, evolved from a turn-one Murkrow: Active \`Ruler of the Night\` denies Tools, Stadiums, and Special Energy from the opponent's hand in addition to the already-applied Item lock.
- Galarian Weezing \`swsh2-113\`, evolved from turn-one Koffing: Active \`Neutralizing Gas\` suppresses opposing Pokémon Abilities other than Neutralizing Gas while the already-applied Item lock persists.
- Stoutland \`bw7-122\`, evolved from turn-one Lillipup with Rare Candy \`sv1-191\`: Active \`Sentinel\` denies opposing Supporters from hand as well as Items through Mysterious Noise.

These are **turn-two** lines. Normally a Basic Pokémon cannot evolve on the turn it enters play, while Rare Candy is available on the second turn and can skip Stage 1.

## Exact event

Fix a 60-card deck containing disjoint named categories in the following order:

1. Elgyem (opening Active);
2. replacement Basic (Murkrow, Koffing, or Lillipup);
3. Beheeyem;
4. replacement Evolution (Honchkrow-GX, Galarian Weezing, or Stoutland);
5. Triple Acceleration Energy;
6. Rare Candy, only for the Stoutland scenario.

All other cards are an undifferentiated remainder. Require:

- at least one Elgyem among the opening seven cards, to start Active with no switching requirement;
- at least one replacement Basic among the opening seven plus the first natural draw, so it can occupy the Bench on turn one;
- at least one of **every** required category by the second natural draw, which occurs on turn two.

If the opponent does not intervene, and there are no additional game restrictions, those cards suffice for the stated handoff. This model allows no search, additional draw, recovery, bonus mulligan draws, switching, or opponent interference. Each copy-count vector defines its own hypothetical deck composition.

Six random Prize cards are put aside after the opening seven. For the two natural draws considered here, integrating over those unknown Prize cards yields the same joint distribution as drawing an ordered pair uniformly from the 53 unseen cards. The calculation therefore incorporates Prize risk marginally, without pretending the player knows their Prizes.

## Results

| Handoff | Engine copy vector | Exact probability |
| --- | --- | ---: |
| Honchkrow-GX, 3 Honchkrow-GX | (4,4,4,3,4) | 0.734846% |
| Honchkrow-GX or Galarian Weezing, 4 copies of the replacement Evolution | (4,4,4,4,4) | 0.940606% |
| Stoutland + Rare Candy, 2 Stoutland | (4,4,4,2,4,4) | 0.150309% |
| Stoutland + Rare Candy, 4 Stoutland | (4,4,4,4,4,4) | 0.281798% |

All figures are exact finite-population probabilities rounded to six decimal places. The event is purposely restrictive. These figures should **not** be interpreted as realistic tournament setup rates, ceilings on optimized decks, or matchup win probabilities.

## Method and validation

\`reproduce.py\` enumerates every multivariate hypergeometric opening-hand composition, followed by every ordered pair of subsequent category draws. If category \`i\` has \`c_i\` copies and opening hand count \`h_i\`, an ordered continuation \`(i,j)\` has multiplicity \`(c_i-h_i)(c_j-h_j-1[i=j])\`. Weight each opening hand by \`product(comb(c_i,h_i))\`, including the remainder category. Retain continuations satisfying the three time-window constraints.

The exact denominator is \`comb(60,7) * 53 * 52\`. The script verifies that every enumerated deal contributes once to that complete sample space, which guards against a common mistake of treating the two turn draws as independent with replacement.

An independent 250,000-trial random sample (seed 61009) yielded 0.942800% for the four-copy Stage 1 scenario and 0.297200% for the four-copy Stoutland scenario, consistent with the exact 0.940606% and 0.281798% probabilities within ordinary sampling error.

Reproduce:

\`python results/beheeyem_handoff_blind_draw/reproduce.py\`

## Strategic interpretation and open questions

Adding Rare Candy as a separate necessary channel sharply reduces blind-draw handoff frequency even when each category receives a full four copies. This quantifies one source of the **Active Move Realism** gap for overlapping lock packages. Mechanically available combinations need a search-and-evolution budget, and a capable search engine can change this comparison substantially.

Next research should evaluate an actual 60-card Beheeyem list with Item searches, Supporter contention, Energy access, turn-one Basic placement, evolving two lines, and the opposing deck's ability to disrupt the board. The key decision is often which replacement lock attacks the opponent's critical action channels. A simple count of restricted card classes cannot substitute for matchup-conditional state analysis.

Do not conflate the retained **opponent-targeted attack effect** with a continuous Ability on Beheeyem: the former persists into the next opponent turn after Beheeyem shuffles away; the replacement's Active-dependent lock lasts only while its source remains effective and Active.
