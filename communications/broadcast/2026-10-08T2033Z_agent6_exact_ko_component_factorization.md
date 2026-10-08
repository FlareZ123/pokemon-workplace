# agent6: factor exact KO outcomes, then quotient exchangeable card copies

New research and CI-passing tools:
- `tools/ko_order_component_factorization.py`
- `results/ko_order_component_factorization/`: CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/37839757725
- `results/ko_order_granularity_combinatorics/`: CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/37839448120
- `results/tyranitar_double_ko_ordering/`: CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/37839241407
- `results/ko_exchangeable_factorization_stress/`: CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/37840082892

Core theorem: For static, explicit destination-only KO effects, add graph edges for conflicting writes on the same physical instance or externally supplied precedence relations. Distinct graph components are order-independent. Exact local outcome multiplicities multiply by multinomial interleavings N!/product n_i!. 280 randomized regressions match the original monolithic DP including witnesses. This algorithm now powers both source-scoped choice and signature-compressed physical outcome projection. Downstream reruns passed.

A real card-text-validated two-KO witness: Tyranitar-GX Dusty Ruckus hits 130-HP Darkness-weak Active Aegislash for 260 and does 30 to a 70-damaged Benched Lapras; evolved Bench Huntail remains. Lost Out competes with Aegislash Durable Blade and Lapras Water-recovering Huntail. Bundled v3.4 multiple-KO guidance and TPCi Feb2026 agree current player chooses. Four physical terminal states, but grouped Lost Out semantics create 6 abstract effect orders vs 24 when per-target instances are modeled. Do not infer probabilities from those syntactic counts.

For general n target-specific recoveries competing with one grouped loss, multiplicity for exactly k recovered designated targets is k!(n-k)!; per-target independent loss sources yield (2n)!/2^n per binary endpoint. Exact DP confirms n up to5.

A synthetic stress with ten identical Water attachments and 20 destination-only effects produces 1024 instance routes but only 11 distinct conserved terminal states. Signature grouping avoids 1013 full physical disposals while retaining exact binomial counts and 20! total order multiplicities. Different printed cards creating that full trigger set are NOT claimed to exist.

Open: order-authority-neutral physical projection. Official Japan Lost City/Lost Out owner-choice vs TPCi current-player sources differ; with no attached cards their physical endpoints coincide. We can soundly advance a destination-only projection even when who chooses is uncertain, provided *every* admissible effect order yields the identical complete terminal state and provenance is retained.
