# Complete same-set print-variant metadata anomaly scan

## Objective

A fixed, guarded list of 72 known flawed print records is useful until the next card snapshot adds a new printing with a similar defect. This research adds an archive-wide, repeatable **candidate generator** that detects gameplay-matched print variants whose stage/subtypes or Rule Box text differ.

The scanner `tools/same_set_print_anomalies.py` compares Pokémon sharing an identical set ID, name, HP, types, evolution, attacks, Abilities, Weakness, Resistance and Retreat Cost. It leaves subtype and rules metadata out of the initial identity signature, then reports groups where either field differs. It does not assume a flag proves an error, since wording can differ harmlessly.

## Observed source snapshot

Across the entire supplied English card archive, the raw same-set scan finds **three** candidate families:

| Set | Same-combat Pokémon prints | Diagnosis |
| --- | --- | --- |
| `me5` | Mega Chandelure ex `me5-38/99/115` | Special-art `115` omitted Stage 2 and Mega three-Prize rule |
| `sv8pt5` | Terapagos ex `sv8pt5-92/169/180` | Regular `92` omitted Tera subtype and Bench-damage immunity |
| `svp` | Charizard ex `svp-56/74` | Same Tera Bench-protection meaning, differing whether rule text includes a `Tera:` prefix |

Applying the shared [verified-card corrections](../verified_card_metadata_boundary/) removes the first two candidate families. The surviving two-promo Charizard variation is recorded deliberately as a *cosmetic rule-label difference*, with matching Tera subtype. We do not rewrite those records, since the scan itself is a candidate-finding tool and automatic word substitution deserves its own proof.

The two previously fixed source omissions would otherwise go undetected on new artwork variants. The group scan preserves their diagnostic signatures in a fast regression that can be rerun whenever `resources/cards/en` changes.

## Reproduction

`python -m results.same_set_print_anomaly_guard.reproduce`

The reproducer verifies the complete raw and normalized issue sets and checks that the surviving Charizard family has only a `Tera:` prefix difference. CI: `.github/workflows/validate-same-set-print-anomalies.yml`, a Windows test.

## Limitations

This scan only compares multiple physical prints in the **same set** with matching combat fields. It does not detect anomalies shared by every variant, errors on unique prints, missing attacker fields, or wrong set/print identity. A result with no newly flagged families therefore does not prove the underlying card archive is complete or correct. Cross-set aliases and user-supplied paper print choices require additional comparison tools.
