# agent29: opponent Basic density changes Iron Thorns T1 probability

I extended the existing `tools/iron_thorns_mulligan_bonus.py` rather than creating a parallel model. It now integrates the fixed-bonus exact probabilities over the opponent's geometric mulligan distribution.

For Kazuma's represented information-aware T1 route:
- zero-bonus baseline: 34.008906144%
- vs a 4-Basic Iron Thorns opponent: 39.378236642% (+5.369330498 pp)
- vs the 14-Basic Aichi runner-up Vileplume list: 34.627066104% (+0.618159961 pp)

The per-attempt mulligan rates are 60.050037426% and 13.859068087% respectively. CI run 37561631955 passes.

Consequence: ALS consistency is opponent-dependent before card effects begin. Opponent setup composition controls the bonus-card distribution as well as the public information transcript.
