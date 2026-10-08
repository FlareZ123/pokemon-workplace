# Empty optional attack fields are schema noise

## Question

Does the bundled card database distinguish gameplay-equivalent reprints because one record stores an empty attack field while another omits the optional field?

## Finding

Yes.

Eight outside-scope Pokémon prints match legal Expanded reprints after canonicalizing only two optional attack-record shapes:

- `damage: ""` becomes an absent `damage` field;
- `text: ""` becomes an absent `text` field.

The eight historical source prints are:

- four Pikachu prints: `base1-58`, `base4-87`, `pl2-112`, `pop2-16`;
- Dark Tyranitar `ex7-19`;
- Darkrai & Cresselia LEGEND `hgss4-99` and `hgss4-100`;
- Shining Celebi `neo4-106`.

Each maps to a legal 30th Celebration Classic Collection reprint under the normalized representation.

## Why the normalization is mechanical

The transformation does not alter printed attack content.

An empty string and a missing optional field both represent the absence of a printed damage value or attack-effect text in the database schema. The normalization removes only those empty optional fields.

No wording equivalence, target interpretation, timing rule, or gameplay inference is introduced.

## Consequence

These eight historical prints become exact current-semantic fingerprint candidates instead of remaining in semantic review.

Shining Celebi is especially useful because its historical singleton deck rule is preserved exactly while its legal matching target `me55c-106` carries the same rule.

## Reproduction

`tools/attack_empty_field_normalization.py` audits the full bundled snapshot for outside-scope prints that gain an exact legal Expanded same-name match solely through this normalization.

`results/attack_empty_field_normalization/reproduce.py` fixes the eight source IDs and checks that the integrated reprint resolver now classifies all eight as exact fingerprint candidates.
