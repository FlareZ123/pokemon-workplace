# Explicit reprint divergence predicates

## Question

Can the repository turn a historical/current wording difference into a machine-readable condition that explains when two same-name printings cease to be functionally equivalent?

## Result

Yes, for a narrow auditable wording family.

`tools/reprint_divergence_predicates.py` scans the official historical reprint benchmark for explicit parenthetical exclusions of the form:

`excluding ...`

It preserves the excluded class as a divergence predicate, compares it with current legal same-name targets, accounts for current name-wide errata, and then asks whether the excluded class has a concrete witness in the current paper Expanded card pool.

Across the 76 historical no-reference Trainer benchmark rows:

- **5** rows contain an explicit exclusion;
- **3** are old Great Ball printings whose printed `Pokémon-ex` exclusion is superseded by current name-wide Great Ball errata;
- **2** are Life Herb printings whose `Pokémon-ex` exclusion is not overridden by the modeled current errata;
- those two Life Herb rows produce the predicate **`target is Pokémon-ex`**;
- current Expanded contains one direct witness in the bundled snapshot, `me55c-108` Scizor ex;
- both `ex5-90` and `ex6-93` therefore have a reachable present-day target-set divergence from current Life Herb.

The scan reproduces the earlier hand-written Life Herb witness while exposing its reason as structured data rather than a one-off assertion.

## Why the Great Ball rows do not become negative evidence

The three Great Ball benchmark rows also literally contain `excluding Pokémon-ex`, but Great Ball appears in the repository's current name-wide official errata catalog.

That authoritative current-text layer takes precedence over the historical printed restriction for present-day play. The scanner therefore records those rows as:

`overridden_by_name_wide_errata`

rather than treating the raw historical text as a current divergence.

This distinction is important. A semantic diff should be computed after authoritative current-text normalization where such normalization exists.

## Reachability

A textual difference only becomes a current functional difference when the format can realize the distinguishing state.

For the Life Herb predicate, the relevant state is:

`target is Pokémon-ex`

The bundled current Expanded pool contains `me55c-108` Scizor ex, whose rule text identifies the historical Pokémon-ex class. Current Life Herb can target it, while the two historical Life Herb printings explicitly cannot.

The resulting divergence is therefore observational in the current format rather than merely syntactic.

## Representation

Each extracted row records:

- historical source print ID;
- card name;
- excluded text;
- normalized divergence predicate;
- status;
- current same-name target print IDs whose text lacks the historical exclusion;
- concrete current witness card IDs when the predicate is reachable.

The current status vocabulary is deliberately small:

- `overridden_by_name_wide_errata`;
- `reachable_current_divergence`;
- `currently_unwitnessed`.

## Evidence classes

**Official historical evidence.** The benchmark rows come from the repository's transcription of the 2012 Modified-Legal Reprint List.

**Current authoritative-text evidence.** Name-wide Trainer errata comes from the repository's official errata overlay.

**Card-text evidence.** The historical Life Herb and Great Ball records preserve the `Pokémon-ex` exclusions, while the current same-name targets do not.

**Format-reachability evidence.** `me55c-108` Scizor ex is directly legal in the repository Expanded model and identifies the historical Pokémon-ex class in its rule text.

## Reproduction

Run:

`python results/reprint_divergence_predicates/reproduce.py`

Expected counts:

- 5 benchmark rows with explicit exclusions;
- 3 overridden by name-wide errata;
- 2 reachable current divergences;
- 0 currently unwitnessed exclusions;
- 1 distinct reachable predicate;
- 1 distinct current witness card.

## Scope and limitations

This is intentionally a small semantic island. It does not attempt to parse arbitrary English card text or prove general reprint equivalence.

The current extractor recognizes explicit `excluding ...` clauses and only has a concrete reachability interpretation for the `Pokémon-ex` class. Other wording families should be added only with similarly explicit semantics and regression witnesses.

The result also does not treat historical compatibility labels as timeless positive evidence. It separates the wording difference from the question of whether the distinguishing predicate is reachable in the current format.

## Next work

Promote the two witnessed Life Herb rows into the resolver's known-negative evidence, then add other small divergence families where the relevant state predicate can be represented and checked without guessing free-form card semantics.
