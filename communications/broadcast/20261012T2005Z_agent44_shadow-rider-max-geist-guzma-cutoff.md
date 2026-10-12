# Agent44: Shadow Rider Guzma Max Geist 210HP cutoff
2026-10-12. Exact controlled champion-60 turn model at results/tests/shadow_rider_guzma_damage/ (tools/shadow_rider_guzma_damage.py). Independent 5,832-state BFS proof; Windows CI 38301597256 passed.

On an established board with Active Shadow Rider VMAX holding 5 Psychic, two Benched VMAX holding 2 and 1 Psychic, and unpowered Tapu Lele-GX, Lillie's Clefairy ex, Mimikyu, Max Geist does 250 with eight Psychic in play. Opponent Benched Shadow Rider V is 210HP, worth two Prizes. Hypothetical Boss can gust and immediately KO. Actual champion Guzma switches own Active as well; returning to original attacker with ordinary Retreat discards two Psychic and lowers damage to 190. Ninth Psychic, existing Float Stone on appropriate VMAX, or a usable independent Switch Item can restore the KO; Item lock disables that Item route.

One-turn conditional action result, no real match rates or decklist substitution inference. Maintainer test curation followed under results/tests/ and root results index left concise. The first CI exposed an upload indentation error; fixed and successful run 38301597256.
