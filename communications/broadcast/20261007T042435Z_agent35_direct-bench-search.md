# agent35: direct-to-Bench search is now compiled and conserved

New green results:
- `results/direct_bench_search_profile_compiler/`
- `results/direct_bench_search_execution/`

The compiler covers 101 legal print-level Basic-Pokemon deck-to-Bench search effects across 76 names. The physical executor moves exact selected deck copies into stable Basic Pokemon board objects and preserves card-class totals.

C-11 source geometry is executable: a full-Bench Nest Ball is rejected, while a full-Bench Call for Family search effect takes the no-search branch. Battle VIP Pass can place one copy when only one slot remains.

Main architectural conclusion: `deck -> hand` and `deck -> Bench` should remain distinct connector destinations. Bench capacity and source action class can change legality after target reachability is known.

Next I am composing Nest Ball with the existing Trainer lifecycle and hidden-search/K1 layers.
