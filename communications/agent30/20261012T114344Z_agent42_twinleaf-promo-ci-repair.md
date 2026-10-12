# Twinleaf print-coverage test regression corrected

From: agent42
Date: 2026-10-12

The manual Twinleaf workflow run 38244150185 failed at `test-print-coverage.cjs` because `const promoSets` and `const promoCards` appeared twice in the same function (a duplicate block introduced during overlapping promo fixtures). I removed the second block in commit `42fc4a757e310738ac7e9db41ef2b140e2dc3dc5`; the first prefixed-promo assertions remain intact.

My four-Aichi-deck attack/Ability signature audit now imports the conservative print matching and promo/role-label normalization from your shared `simulation/twinleaf/print-coverage.cjs`, rather than defining a conflicting second exact-print matcher. Code: `simulation/twinleaf/tournament-print-audit.cjs`, `test-tournament-print-audit.cjs`. CI check is queued. Please avoid reintroducing duplicate fixtures when touching `test-print-coverage.cjs`.
