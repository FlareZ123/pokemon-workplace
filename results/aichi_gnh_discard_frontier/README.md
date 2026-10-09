# Aichi Guzma & Hala payment frontier

## Question

The established Aichi post-Guzma & Hala Prize-reset studies originally searched Technical Machine: Evolution and Jet Energy without charging G&H's two-card optional discard. Does requiring a legal discard payment invalidate the headline first-turn endpoint or Ticket-access feasibility rates?

Tool: tools/aichi_gnh_discard_frontier.py
Exact fixtures: reproduce.py
Sample: run.py
Workflow: .github/workflows/validate-agent4-aichi-gnh-discard.yml
Passing run: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37832464099

## Method

For each accepted 7-card opening and first-turn draw, the existing Aichi preparer selects the starting Active and produces a candidate G&H route. Whenever the TM: Evolution or Jet Energy output is not already held, G&H requires discarding exactly two available hand cards before obtaining the needed Tool and Special Energy. Every physically selectable *card-name pair* is enumerated, respecting duplicate counts.

A conditional G&H output succeeds when the needed Tool and Energy are already held after payment or can be fetched from the un-Prized deck. The optional Stadium output, Artazon, is fetched independently if available.

Each payment line is tested against the named board objective via the existing endpoint predicate. For every Ticket/Map tech assignment, the model asks whether at least one valid payment retains a Ticket for an informed first reset or the two Tickets plus one Map required for an informed second reset.

The selection is per-game-state, per-endpoint, and per-tech-package. It is a **hindsight-feasibility upper bound** because the G&H discard must precede its revealing full-deck search and because each payment may consume resources valuable on future turns.

## Results

The fixed 200,000 raw shuffled orders, seed 20261008, generated **172,283** accepted openings. Of these, **121,257** had a G&H route whose optimistic TM and Jet outputs were both available. Each of these 121,257 states admitted at least one legal two-card payment, or no payment was necessary because both resources were already held.

The optimistic and payment-aware **existence** rates coincided across the represented named first-turn endpoints, including the dual Pidgeot/Stoutland Stage 2 objective:

| Endpoint | Original optimistic rate | Payment-feasible existence rate |
| --- | ---: | ---: |
| Dual Stage 2 | 41.72960% | 41.72960% |

Ticket-access existence after legal payment likewise matched nominal access for all shown packages, including:

| Tech package | Nominal/paid first-reset access | Nominal/paid second-reset access |
| --- | ---: | ---: |
| One Ticket | 8.40245% / 8.40245% | 0% / 0% |
| Two Tickets + one Map | 15.88781% / 15.88781% | 0.07314% / 0.07314% |
| Three Tickets + one Map | 22.67374% / 22.67374% | 0.19271% / 0.19271% |

All rates use accepted openings as denominator. This supports *legal payment feasibility* within the simplified ALS. It does not certify a single observation-consistent pre-search discard policy, and it does not prove that the discard is strategically harmless.

## Relationship to the later studies

[aichi_jirachi_payment_frontier](../aichi_jirachi_payment_frontier/) extends this payment family to the chance that a **saved late Stellar Wish** finds an Item. Some payments change the remaining deck's size by discarding a held Tool and retrieving another copy, affecting draw density.

[gnh_tool_thinning_information](../gnh_tool_thinning_information/) proves a distinct risk: a K0 player may not know whether the backup Tool is among the six Prizes before paying G&H. Blindly thinning can lose a guaranteed setup resource, while known-safe thinning improves Ticket density.

The zero initial endpoint-feasibility gap here is consistent with a nonzero *secondary late-Wish* value gap. These are different objectives.

## Limitations

The Aichi preparer excludes many competing Trainer sequencing actions and ignores wider matchup strategy, Lock effects after setup, resource recovery, and alternative paid search routes. Endpoint predicates are narrow first-turn access conditions and omit actual game outcomes.

The model protects no strategically important singleton by default; callers can supply protected names, but it does not infer state-dependent discardability. It assumes accurate physical deck composition for testing whether a searched replacement exists.

This investigation is recorded separately because the relevant tool, CI, and raw result existed before the current agent4 incarnation but did not have a human-readable result README.
