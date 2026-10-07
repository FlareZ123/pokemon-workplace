# Legacy Pokémon Tool category normalization

Current paper rules treat older Pokémon Tools as Pokémon Tools even when their printed template described them as Items.

The bundled snapshot contains 211 legal Expanded Tool prints across 167 names with obsolete generic Item-play text. Thirty of those prints also carry both Item and Pokémon Tool subtypes. The affected records span Black & White (22), XY (60), Sun & Moon (60), and Sword & Shield (69).

The normalizer in tools/tool_category_normalization.py removes Item only when Pokémon Tool is also present, and removes only the two exact historical generic Item-play sentences. Other subtype markers and card-specific rules are preserved.

This matters for typed analysis because the stale Item subtype can incorrectly make a Pokémon Tool satisfy an Item predicate. Forest Seal Stone (swsh12-156), for example, should normalize from Item + Pokémon Tool to Pokémon Tool. Rapid Strike Scroll of the Flying Dragon (swsh7-153) retains Rapid Strike + Pokémon Tool.

The legal gameplay-fingerprint count drops from 10,416 to 10,415 after normalization. The one merge is concrete: the Sword & Shield-era Choice Belt records with stale Item + Pokémon Tool metadata normalize to the same current fingerprint as `sv2-176` Choice Belt. Historical exact reprint candidates remain 106 when this layer is composed into current-semantics comparison.

Evidence: the Advanced Player's Rulebook states that Sword & Shield-and-earlier Pokémon Tools that had Item printed on them are not treated as Items. The current official TCG Errata resource records the same category migration as applying to all previously printed Pokémon Tools.

Reproduce with:

python results/tool_category_normalization/reproduce.py

Limit: this layer does not remove older attachment restrictions or rewrite arbitrary Tool text. Those can carry real gameplay meaning and require separate semantic analysis.
