# Prismatic Evolutions Terapagos ex: missing Tera status and Bench protection

## Verified source error

The bundled `resources/cards/en/sv8pt5.json` contains three same-set printings of a 230-HP Colorless Terapagos ex with exactly the same attacks, Energy costs, type, Weakness, Retreat Cost, and Pokémon-ex Prize rule. The special-art prints `sv8pt5-169` and `sv8pt5-180` correctly include:

- subtype `Tera`;
- the continuous rule protecting this Pokémon from attack damage while on its Bench.

The regular double-rare printing `sv8pt5-92` lacks both fields. Independent published physical-print card transcriptions confirm that **PRE #092 also has Tera status and Bench damage immunity**:

- [Limitless, Terapagos ex PRE 92](https://limitlesstcg.com/cards/PRE/92)
- [TCG Collector, PRE 092/131](https://www.tcgcollector.com/cards/47126/terapagos-ex-prismatic-evolutions-092-131)
- [Same-set reference PRE 169](https://www.pokemon.com/fr/jcc-pokemon/cartes-pokemon/series/sv8pt5/169)

This is a verified card-source omission, rather than two distinct gameplay variants.

## Game consequence

Area Zero Underdepths (`sv8pt5-94`) provides up to eight Bench positions to a player who has **any Tera Pokémon in play**. The old database representation marks the regular Terapagos ex printing as Basic/ex, so a naïve predicate check fails. With the corrected `Tera` tag, that printing satisfies the Stadium's condition. The missing printed Tera rule also otherwise causes models to incorrectly permit attack damage to that card while Benched.

This study proves a metadata discrepancy and a direct rule-predicate consequence. It does not estimate a deck's match performance or establish that any existing headless simulator already consumes these specific shared interfaces.

## Correction and safeguards

`tools/verified_tera_metadata_repairs.py` corrects only `sv8pt5-92` using guarded exact print ID, name, supertype, 230 HP, Colorless type, stage and rule text. It accepts either independently corrected field, allowing idempotent operation if the upstream archive is partially repaired. Unexpected field values fail rather than being overwritten.

Both `tools/deck_validator.py` and `tools/current_card_semantics.py` apply this correction before interpreting a card. Original JSON remains untouched.

## Reproduce

`python -m results.verified_tera_semantics.reproduce`

Tests independently check original fields, both reference printings, four partial-correction states, identical canonical fingerprints, deck-validation records, idempotence, preservation of unrelated records, and the concrete Area Zero Tera predicate. Windows CI is defined in `.github/workflows/validate-verified-tera-semantics.yml`.

## Audit reach

A same-set search grouping Pokémon by substantive combat fields initially found three families with divergent subtype/rule metadata. One was this Terapagos case, one the already corrected Mega Chandelure ex, and one Charizard ex `svp-56`/`svp-74` with equivalent Bench protection wording but differing `Tera:` prefix. This scan does not prove that the entire card archive is free of additional metadata errors or that all candidate families warrant normalization.
