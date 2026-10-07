# Alolan Muk Basic-Ability suppression surface

## Question

How large is the self/opponent Ability surface affected when Dream Ball puts Alolan Muk `sm1-58` directly into play and Power of Alchemy becomes active?

The affected legal Basic-Pokémon Ability pool is large, including many historically important Expanded support engines.

Implementation: `tools/alolan_muk_basic_ability_surface.py`  
Regression: `results/alolan_muk_basic_ability_surface/reproduce.py`

## Card-text basis

Alolan Muk's Power of Alchemy says that each Basic Pokémon in play, in each player's hand, and in each player's discard pile has no Abilities.

This is symmetrical. The Dream Ball player does not receive an exemption.

The official Advanced Player's Rulebook uses Power of Alchemy as an example of an effect that removes rules text, confirming that affected Basic Pokémon are treated as having no Abilities while the effect applies.

## Audited surface

Across the current effectively legal paper-Expanded card pool, the audit finds:

- 1,103 exact Basic-Pokémon Ability rows;
- 1,103 exact prints represented;
- 420 unique card names with at least one Ability.

A narrow lexical geometry split gives:

- 743 in-play or otherwise unspecified rows;
- 168 Active-required rows;
- 52 Bench-required rows;
- 123 hand-to-Bench trigger rows;
- 17 off-board-zone rows.

The 123 hand-to-Bench rows span 48 unique card names.

Those 123 rows are especially relevant to sequencing because Power of Alchemy removes the Ability while the Basic Pokémon is still in hand and continues removing it after the card enters play.

## Named support witnesses

Tapu Lele-GX `sm2-60`, Wonder Tag, Dedenne-GX `sm10-57`, Dedechange, and Crobat V `swsh3-104`, Dark Asset are exact legal Basic-Pokémon Ability rows in the audited pool and all three fall into the hand-to-Bench trigger class.

Shaymin-EX Set Up prints `xy6-77`, `xy6-77a`, and `xy6-106` are excluded because those prints are currently banned in Expanded.

## Strategic consequence

Dream Ball into Alolan Muk creates an immediate sequencing deadline for Basic Ability support on both sides.

A player planning to use Wonder Tag, Dedechange, Dark Asset, or another affected Basic Ability should treat the Muk entry point as a boundary after which those Ability lines are unavailable while Power of Alchemy remains active.

This creates a connector-domination and AMR interaction. Dream Ball can bypass the Alolan Grimer evolution requirement and deny the opponent's engine, while the same suppression can delete the Dream Ball player's remaining Basic support lines.

The value of the lock therefore depends on what has already been consumed or established. A Basic support Pokémon can move from high strategic value before Muk to effectively dead Ability text after Muk.

## Limits

The geometry classifier is lexical and does not model every Ability timing form.

The 1,103 rows are exact prints, so reprints and equivalent gameplay variants can contribute multiple rows.

This result catalogs the Ability surface Power of Alchemy can remove. It does not quantify the matchup value of suppressing each row, how often those cards appear in decks, or the cost of turning off the Dream Ball player's own support.

A stronger follow-up is an executable sequencing model that compares "use Basic support first, then establish Alolan Muk" against "establish Alolan Muk first" for specific hand and board states.
