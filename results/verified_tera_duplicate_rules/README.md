# Duplicate Tera Bench-protection rule in 24 print records

## Finding

The card archive contains **24 English Tera Pokémon ex prints** whose `rules` lists contain the same Bench attack-damage prevention twice:

- 4 `sv5` Temporal Forces records.
- 20 `sv6` Twilight Masquerade records.

The first rule is the standard text, while the third repeats the same text with `Tera:` in front. The intervening second rule is the ordinary Pokémon ex two-Prize rule. Printed card fronts present the Tera protection statement **once** and the ex rule **once**.

Two independent physical card-front examples:
- [Wugtrio ex TEF 60](https://totalcards.net/products/pokemon-scarlet-violet-temporal-forces-wugtrio-ex-060-162)
- [Dragapult ex TWM 130](https://totalcards.net/products/pokemon-scarlet-violet-twilight-masquerade-dragapult-ex-130-167)

The later Prismatic Evolutions `sv8pt5-73` Dragapult ex printing already has the two-rule representation. The two Dragapult variants have exactly the same substantive attacks, HP, type, Stage, Weakness, Resistance and Retreat Cost.

## Consequence

The double entry does not independently stack its “prevent all damage” effect in ordinary gameplay: preventing damage twice is the same material outcome as preventing it once. The duplicate nevertheless creates an artificial gameplay-fingerprint difference between the 2024 `sv6-130` and newer `sv8pt5-73` printings. It can also lead an effect inventory to count duplicate protection sources.

`tools/verified_tera_duplicate_rules.py` uses an exact 24-print allowlist and checks Tera/ex subtypes plus the literal three-rule sequence. It removes the second identical effect. All unexpected mutations fail closed; already-corrected inputs are unchanged. Source JSON stays unmodified.

Both `tools/current_card_semantics.py` and `tools/deck_validator.py` apply this print-local repair before reading semantic identity or card metadata.

## Reproduce

`python -m results.verified_tera_duplicate_rules.reproduce`

The regression checks the exact 4+20 affected prints, frozen allowlist equality, immutability, idempotence, downstream pipeline consistency, corrupted-source guards and cross-set Dragapult ex semantic equivalence. Windows CI: `.github/workflows/validate-verified-tera-duplicate-rules.yml`.

## Research scope

This is data hygiene and semantic deduplication evidence. It does not grant historical reprint legality to pre-BW printings, nor does it demonstrate a match-win effect. An exhaustive physical card-front audit of all art versions remains beyond this specific sample.
