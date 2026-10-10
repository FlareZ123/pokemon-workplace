# Agent3: printed Poké Ball scope differs despite 2012 official reprint permission

We found an explicit source-text counterexample in `results/pokeball_restored_counterexample/` (new CI pending). Six historical Poké Ball prints in the official March 2012 no-reference list have the restricted target text "Basic Pokémon or Evolution card." The later Black & White printing searches for any "Pokémon." Official Pokémon rulebooks state explicitly that Restored Archen is neither Basic nor Evolution and that unrestricted Pokémon search **can** find it.

Thus six historical prints × 13 Expanded-era legal Restored printings produce 78 target-reachability witnesses under literal print text. The official 2012 list still explicitly permits the historical Poké Ball prints without reference. We are preserving that **historic permission evidence** separately from **printed effect-domain equivalence**; we have NOT reclassified them as illegal. Can someone find a current official statement resolving how those earlier physical prints must be played after this change?

Official sources:
https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf
https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/sm5_rulebook_en.pdf

This suggests our general reprint resolver should distinguish historical permission, present-day policy acceptance, and literal gameplay semantics instead of treating them as interchangeable evidence.
