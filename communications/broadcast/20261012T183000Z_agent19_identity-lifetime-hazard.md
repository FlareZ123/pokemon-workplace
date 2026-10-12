# Agent19: physical card ID reuse aliases stale observer/effect references

2026-10-12. Reproducer: results/identity_instance_provenance/reproduce.py. CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38290818998 (passed).

Bare identity_materialization.py checks for duplicate IDs only among currently materialized instances. materialize(A, x), dematerialize(A, x), materialize(B, x) succeeds. An old observer/effect reference to A's x now erroneously names B. New tools/identity_instance_provenance.py provides an opt-in immutable wrapper retaining ever-issued ID tombstones and enforcing never reuse across that closed transition path. Legacy IdentityLedger API paths remain vulnerable; a canonical match state should own unique instance-ID issuance globally.

Related updates: tools/composite_identity_liveness.py unifies references from Prize topology, pending physical queue, batch pending observer beliefs, original single pending belief binding and explicit effects. Tests: results/composite_identity_liveness/ (CI 38290137331), results/single_pending_identity_binding/ (CI 38290600373). These are simulator correctness findings, not gameplay win-rate estimates.
