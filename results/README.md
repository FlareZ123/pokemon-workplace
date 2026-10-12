**Both players can safely reuse local instance and reference names in two-ledger match models:** [Player-scoped identity liveness](match_scoped_identity_liveness/) preserves `(player_id, reference)` ownership; Player A's exact hand effect holds A's card without spuriously blocking Player B's equally named physical copy. Two independently conserved three-card ledgers, stale snapshot rejection and invalid-player checks pass [CI 38291296089](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291296089). This is a match-state correctness building block, not a simulated win rate.

Deleted by repository owner.
Next agent should reorganize the results page into `tests/` and have all of the current spam of tests in there, and have a folder for every deck that is being tested, so:
results/
       tests/
            ability_lock_causal_state/
            ability_lock_setup_precedence/
            ...
       decks/
            regidrago-variant-1/
            regidrago-variant-2/
            vileplume-control-variant-1/
            ....
  the readme should explain the current best decks and should be no larger than 10K words, it can border +-3K.
  never again make a "slop" folder that is just a spam of tests, this file should be continuously rewritten and refined and trimmed.
  Keep this repo maintainer directive in a footnote preserved, and rewrite the whole readme.
