# Unresolved historical Trainer reprint frontier

The central reprint resolver partitions older Trainer prints sharing names with legal paper Expanded cards into evidence types. As of the October 2026 bundled archive, there are 168 relevant pre-Black & White Trainer print records. Positive candidate states and known non-equivalent states account for 147; the residual `semantic_review` group has **21 print records**, representing the smallest bounded region for evidence-driven follow-up studies.

The reproducible `reproduce.py` enumerates these actual print identities using `tools/reprint_errata_resolution.py`, groups them by card name and prints their legal Expanded counterpart IDs. It requires the exact baseline counts to catch resolver and source-database drift.

The state label `semantic_review` means the repo has not established a sufficient equivalence/nonequivalence witness. It does not mean the print is illegal, and similarity of name or English text alone does not certify tournament acceptance. Follow-up work should prioritize card text, timing, target domain and rule-category effects; the [historical Maintenance bridge](../maintenance_shuffle_equivalence/) illustrates a completed positive case.

Run `python -m results.trainer_semantic_review_frontier.reproduce` or the Windows `.github/workflows/validate-trainer-semantic-review-frontier.yml`.
