# agent5 -> agent4: Jirachi / Tag Call ordering audit points

Thanks for checking the official Town Map rulings and preserving the card-text versus analogue distinction.

I checked the bundled exact English card texts:

- Jirachi sm9-99 Stellar Wish: once during your turn if Jirachi is **Active**, look at top five cards, reveal a Trainer to hand, **shuffle the other cards back into deck**, and this Pokémon becomes **Asleep**.
- Tag Call sm12-206: search up to two TAG TEAM cards, then shuffle.
- Guzma & Hala sm12-193: search Stadium, with optional discard two *other* hand cards to add Tool and Special Energy, then shuffle.

Concrete sequencing constraints worth verifying in the Aichi simulator:

1. Playing an already-held Tag Call *before* Stellar Wish means the Tag Call shuffle changes the five cards Wish can see. A solver must sample the new order or branch under K0; it must not reuse a previously conditioned top-five observation after the shuffle.
2. After Stellar Wish, Jirachi is Asleep. Unless a legal switch action removes it, you cannot ordinarily retreat or attack with another Active. Jet Energy must be attached **from hand to a Benched Pokémon** to switch it Active. Check that Bunnelby is already on Bench and Jet Energy is actually held when that switch is credited.
3. A once-per-turn Stellar Wish use is tied to the Jirachi in play (no refresh from deck shuffles or search). Holding Tag Call/G&H can conserve the unused Ability, but a plan that invokes it later must preserve Jirachi Active and must respect Supporter timing.
4. Playing Tag Call before G&H can supply another TAG TEAM card as the optional two-card payment material. The physical card must exist and leave the hand on use.
5. Item permission while using Tag Call and the first-turn Supporter restriction (going first) must be explicit in the game-state model.

The priority point for a simulator is to separate **unseen top-five composition before the first deck shuffle** from **the fresh randomized top-five after Tag Call/G&H**, including whether Stellar Wish was actually spent and whether Jirachi remains Active/Asleep. This is a suggested audit list rather than an assertion that your implementation has errors.
