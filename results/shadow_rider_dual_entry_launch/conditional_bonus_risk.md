# When already holding both entry triggers, an optional bonus draw can reduce VMAX launch reliability

## Fully specified opening information

Suppose the Shadow Rider champion player has a valid seven-card opening that already contains:

- Radiant Eternatus, which must stay in hand to activate Climactic Gate;
- Tapu Lele-GX, which must stay in hand to activate Wonder Tag;
- a separate unrelated Basic starter, which can occupy the Active Spot;
- no Shadow Rider Calyrex VMAX among the seven opening cards.

Assume the rest of the hand is irrelevant to this narrowly defined entry endpoint, that the player reserves enough Bench capacity, and that Items/Abilities are not locked. The player can perform Wonder Tag first, then play Radiant, and needs at least **two** of four VMAX still searchable in the deck. This is an illustrative *conditional opening category*; it does not assert every full-board consequence is favorable.

The opponent has mulliganed once, so the player may choose whether to draw an extra bonus card during setup. Both choices later receive the normal natural draw going second.

## Exact comparison

| Decision | Probability at least two VMAX remain in deck |
| --- | ---: |
| Decline optional bonus, take one natural draw | **99.438231025356%** |
| Take one optional bonus, then one natural draw | **99.115512678221%** |
| **Lost two-VMAX availability from taking bonus** | **0.322718347136 percentage points** |

The exact loss fraction is **189/58,565**. There are no access gains for this narrowly defined *already-held entry pair*, because Radiant and Lele and an Active Basic are in hand before the bonus. The extra card may of course improve unrelated strategies or be needed to pay other resource costs, which the decision does not value.

## Probability proof and physical oracle

Conditioning on zero VMAX in the original seven leaves four distinct VMAX among the other 53 physical cards. Six of those 53 form Prize cards. After Prize placement, 47 remain in the initial draw deck.

Let p be the number of VMAX Prized. Under uniform hidden Prize assignment:

\`P(p=j) = C(4,j) C(49,6-j) / C(53,6)\`.

For d draws from the 47 remaining cards, given p, the probability exactly t VMAX are drawn is

\`C(4-p,t) C(47-4+p,d-t) / C(47,d)\`.

The requested two-VMAX survival event is \`4-p-t >= 2\`. Summing these exact rational weights gives the table for d=1 and d=2.

The extra draw specifically causes a previously possible launch to fail when the first natural draw would leave exactly two VMAX in deck and the additional card is a VMAX. The general coupled gain/loss result is documented in [bonus_draw_reversal.md](bonus_draw_reversal.md).

The [conditional kernel](../../tools/shadow_rider_conditional_vmax_draw.py) uses these hypergeometric formulas. The independent [physical-position reproducer](conditional_bonus_reproduce.py) enumerates **all C(53,4) physical placements** of the VMAX cards among the 53 unseen slots, treating the first six slots as Prizes and the next two as potential draws. It exactly matches both success probabilities and the loss fraction, alongside three smaller independent parameter tests.

## What this means for play decisions

For a player assessing *only the immediate Climactic Gate double-VMAX target*, the extra draw slightly reduces success in the described opening because it cannot provide a needed entry Pokémon and it may consume a critical deck-resident target. Real turn-one play values cards for other reasons, and available Supporters, searches, future Energy, opposing matchups, or the wish to draw more cards may reverse that preference. The 0.3227 percentage point is a conditional combinatorial effect and should never be presented as a measured net match-win change.

The repository's broader opponent-mulligan policy model can use this result to avoid assuming every target-restricted deck-search success probability is monotonic in bonus draws.
