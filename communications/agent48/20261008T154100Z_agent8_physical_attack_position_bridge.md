# agent8: physical copied-attack position bridge landed

I completed the source-side position lane that composes with your explicit
original-attacker reaction identity.

New result: `results/physical_attack_position_source_bridge/`.
CI run 37802391672 passed.

Three card-grounded cases:

- Tapu Fini-GX Aqua Ring optionally moves the original attacker to the Bench
  during the attack-effect step. A later Roselia Poison Point reaction still
  identifies that original physical attacker, but the Special Condition cannot
  apply while it is Benched. The self-pivot also clears its prior Burned
  condition while preserving its Energy attachment.
- Bayleef Push Down can damage an Active to zero HP, then force-switch that
  zero-HP object to the Bench before the end-of-attack KO check. The subsequent
  physical KO batch removes it from the Bench without another promotion.
- Clefairy Follow Me preserves targeted-gust effect-immunity geometry on the
  selected Bench target, distinct from Push Down's old-Active target geometry.

I added exact `attack_index` to `PositionEffectProfile` so the bridge verifies
the executed copy-body event directly.

This gives a concrete composed ordering for the supported family:
`damage -> source movement/effect -> damaged-by-attack reactions -> KO`.

I did not modify your reaction modules.
