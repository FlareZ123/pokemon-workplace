# Exact physical search-to-execution policy

## Question and result

A search target reaching hand is insufficient to establish a same-turn tactical line. The search card can consume the Supporter quota or a required discard payment can consume the resource the planned continuation needs.

\`tools/physical_staged_trainer_policy.py\` evaluates at most one already-compiled Trainer retrieval branch, including its physical source card, exact discard selection, retrieved targets, turn budget, lock channels, and downstream generic Trainer execution deadlines. Every alternative uses \`execute_trainer_retrieval_transaction\`, preserving card-class totals. A no-action branch prevents needless spending. Selection maximizes completed execution units, then prefers lower discard and fewer actions.

The reproducer uses actual bundled English prints for Computer Search (\`bw7-137\`), Green's Exploration (\`sm10-175\`), and Boss's Orders (\`swsh2-154\`). Computer Search's unrestricted search is deliberately narrowed here to the available Boss target; Green is considered with its no-Ability-Pokémon condition satisfied.

## Controlled state results

| Hand, quota, and continuation | Selected route |
| --- | --- |
| Computer Search, Green and two disposable cards; Boss in deck; one Supporter slot | Computer Search, paying both physical discard cards, preserves Boss's same-turn execution slot |
| Computer Search, Green, one disposable card and a strategically protected card | No branch completes the same-turn Boss objective under that explicit discard policy |
| Computer Search with just one other hand card, even if its own source is listed as discard candidate | No executable Computer Search payment |
| Green and two Supporter slots | Green retrieves Boss, leaving one Supporter play |
| Search attempted after attack | Closed action window rejects |
| Boss already held | No search is needed |

The protected-card case is a strategic retention assumption expressed by a zero-copy discard limit, rather than a universal prohibition on discarding the named card.

## Interpretation

The exact state model fixes the physical-resource caveat left open by \`results/staged_trainer_objectives/\`. The same abstract output can have sharply different completion value depending on source card availability, legal discard witnesses, and reserved Supporter slots. This is a rules-valid deterministic witness. It is not a complete card-effect execution, head-to-head simulation, or estimate of match strength.

Future tests should sample real 60-card hands and Prizes, score concrete matchup-specific tactical continuations, and couple selected transactions to the multi-action sequencing already demonstrated in \`results/sequential_trainer_replenishment/\`.

Reproduce using \`results/physical_staged_trainer_policy/reproduce.py\`, or the manual Windows CI workflow \`.github/workflows/validate-physical-staged-trainer-policy.yml\`.
