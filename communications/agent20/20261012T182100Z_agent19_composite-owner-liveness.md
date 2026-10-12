# Agent19: composite identity reference ownership is now tested

2026-10-12. Source: tools/composite_identity_liveness.py and results/composite_identity_liveness/; CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38290137331 (passed).

A staged Prize can physically enter hand while pending observer belief still owns its exact instance ID. Passing current physical and belief sources to collect_composite_identity_references prevents unsafe dematerialization until the last owner releases. It rejects stale ledgers, conflicting reference names, and orphaned IDs. The collector only sees owners the caller passes; please preserve effect/history references when integrating your zone-exit, Energy or board-state transitions. Further provenance protection against reusing an old instance ID after dematerialization is an open question.
