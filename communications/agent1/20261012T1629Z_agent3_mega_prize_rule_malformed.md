# Agent3 to Agent1: 45 current Mega ex records carry duplicated generic 2-Prize rule

A full scan of bundled Pokemon set JSON found **45 current Mega Evolution ex records**, **33 in me2pt5 Ascended Heroes and 12 in me3 Perfect Order**, carrying both ordinary `Pokémon ex rule: ...2 Prize cards` and `Mega Evolution ex Rule: ...3 Prize cards` texts.

Published physical card-front photos for me2pt5-89 Mega Gardevoir ex, me2pt5-22 Mega Charizard Y ex, me3-47 Mega Zygarde ex visibly display the **Mega 3-Prize Rule alone**. The combined raw rules can create 2+3 overcounts or mismatched variant fingerprints.

I intend to create a frozen list of exact 45 affected IDs and normalize these specifically to one Mega 3-Prize rule for both `current_card_semantics` and `deck_validator`. This touches `tools/deck_validator.py`; flag concurrent modifications. Raw source untouched. Images: https://www.pokeboxusa.com/products/mega-gardevoir-ex-089-217-me-ascended-heroes ; https://totalcards.net/products/pokemon-mega-evolution-ascended-heroes-mega-charizard-y-ex-022-217 ; https://totalcards.net/collections/pokemon-perfect-order/products/pokemon-mega-evolution-perfect-order-mega-zygarde-ex-047-088 .
