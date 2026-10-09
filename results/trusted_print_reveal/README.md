# Source-backed public card-print provenance in an exact physical search

## Problem

Physical search simulations need a stable mapping between a materialized card's declared exact-print class and the card that actually exists in the paper Expanded card pool. A model can correctly conserve cards and bind a public observation to the searched instance while still accepting an internally inconsistent instance such as:

`CardInstance(card_class="exact_print:xy1-42", card_name="Porygon")`.

That pair should be rejected: the bundled legal print `xy1-42` is a Pikachu. The print class is supplied by a caller, so it cannot alone prove the record's name, effective legality, or actual printed identity.

## Implementation

`tools/trusted_print_reveal.py` provides `validate_materialized_print(instance, identity_index, require_legal=True)`.

It reuses the established `tools/card_identity.py` index, which already applies the repository's current effective paper Expanded legality baseline and retains a print's catalog name. The validator checks:

1. The material class has the `exact_print:<ID>` namespace.
2. The print ID exists in the Expanded-scoped catalog.
3. The materialized displayed name agrees with the catalog record.
4. Its effective paper Expanded status is Legal, unless a caller explicitly relaxes the legality requirement for research.

The exact `execute_hidden_trainer_search_transaction` bridge now accepts an optional `print_identity_index`, and validates its newly materialized searched instance against the source catalog before updating observer beliefs. The composed `execute_coarse_revealed_trainer_search` also forwards this optional index.

Ordinary existing callers without an index preserve their behavior; the extra source validation is opt-in. Source-backed name and legality binding is especially useful for exact-print simulation results that purport to use real tournament cards.

## Concrete validation

The regression loads the complete local identity index and verifies:

- legal `xy1-42` Pikachu and `swsh7-49` Pikachu have the same printed name but different conservative gameplay variants;
- exact-print identity resolves to the correct card while name namespace projects both to Pikachu;
- fake name Porygon attached to Pikachu's exact-print ID is rejected;
- an unknown exact-print ID is rejected;
- one catalog print with effective status Banned is rejected by default, while an explicit non-legality audit can still resolve its provenance;
- the existing full Quick Ball physical/latent opponent regression passes with the authoritative catalog supplied;
- the composed bridge rejects source-inconsistent materialized name even when the caller's public label is separately supplied as Pikachu.

## Reproduction

- Validation helper: `tools/trusted_print_reveal.py`.
- Physical search: `tools/trainer_search_hidden_state_bridge.py`.
- Coarsened physical search: `tools/revealed_search_coarse_physical_bridge.py`.
- Test: `results/trusted_print_reveal/reproduce.py`.
- CI: `.github/workflows/validate-trusted-print-reveal.yml`.

## Scope

The print identity index is the repository's current local snapshot and current effective-legality model. Official reprint equivalence and future ban updates remain separate questions. This validation checks print/name/status provenance, and does not replace behavioral policy feasibility, energy/attack legality, tournament deck construction, or complete turn sequencing.

Future extensions should validate attached exact-print instances in other public card zones through the same catalog, so opponent inference can reliably connect a revealed physical card's documented gameplay text with its position.
