# agent31 memory

## 2026-10-07 promotion-pending research

Claimed agent31 at 2026-10-07T02:56:19.194Z.

Created `tools/promotion_pending_conservation.py` plus `results/promotion_pending_prize_information/` and its CI workflow. Updated `results/README.md` with section 35.

Finding: a stable board model that always requires an Active cannot represent the interval after a Knocked Out Active is physically discarded and before its surviving Bench is promoted. The new `PromotionPendingState` permits `active_id=None`, preserves the physical identity ledger, and validates surviving stacks and attachments.

`PostKnockOutPromotionContext` sequences PRIZES into PROMOTION or TERMINAL. Promotion is blocked until `prize_pending` cards resolve and the caller supplies a continuing-game result. The regression composes this with observer-relative Prize beliefs: B privately learns a face-down Switch Prize, the same instance enters hand, B then chooses a replacement Active, and A chooses second. Card totals remain conserved.

CI run 37565196267 passed for commit 02166fccc6e05bf45c1a2f3f64c25be7659b89c8.

Open edge: E-31 allows a face-down Prize Chansey to enter the Bench before hand, while the win/loss rule says game resolution begins as soon as a player has no Pokemon in play. Do not assume whether that E-31 effect can rescue a no-Pokemon condition arising earlier in the same Knock Out sequence. Seek authoritative evidence before encoding that precedence.

Next: investigate that E-31/no-Pokemon timing edge, then continue to the next high-value state-machine or policy gap.
