# Copied attack Energy disruption before damage reactions

## Question

If a copied attack deals damage and then discards an attached Energy during
the attack-effect step, can removing Spiky Energy suppress its later
damaged-by-attack backlash?

## Rule timing

The Advanced Player's Rulebook resolves attack damage before effects outside
damage, then resolves effects that activate when a Pokemon is damaged, and
only afterward checks for Knock Outs.

Its Gastro Acid example makes the consequence concrete: an Ability removed by
the attack during the effects step does not activate in the later
damaged-by-attack step. This result applies the same timing principle to an
attached Energy effect.

## Source contract

The existing one-Energy disruption compiler now preserves exact attack index
and exposes its complete-text attack parser. The whole-attack coverage
inventory classifies 191 attack profiles as `exact_energy_disruption`.

`tools/physical_attack_energy_disruption_source_bridge.py` verifies the exact
copied body event and delegates physical attachment removal to the conserved
Energy-disruption executor.

## Hyper Beam and Spiky Energy

The main regression copies Duraludon `me2-74` Hyper Beam through Team Rocket's
Persian ex Haughty Order. The defending Active has both Spiky Energy and a
Basic Energy attached.

Immediately after Hyper Beam's 70 damage, Spiky Energy is a live potential
reaction source. During step 5:

- discarding Spiky Energy itself leaves no Spiky reaction in step 6;
- discarding the Basic Energy leaves Spiky attached, so step 6 places two
  damage counters on the physical attacking Pokemon;
- attack-effect immunity on the defending Pokemon blocks Hyper Beam's discard,
  leaves Spiky attached, and therefore preserves the later backlash.

This demonstrates that reaction-source eligibility must be read from the board
after applicable attack effects have resolved.

## Coin-gated selected target

Gothorita `bw2-46` Deleting Glare provides the second witness. Tails leaves
the physical attachments unchanged. Heads, with an explicit target Pokemon and
Energy instance, discards that exact attachment.

## Conservation

Attachment removal uses the shared identity-aware Energy-disruption executor.
The removed Energy leaves the Pokemon stack and enters discard while card-class
totals remain conserved.

## Limits

This bridge covers the compiler's exact one-Energy attack bodies. Multi-Energy
discard, Energy-type-specific text outside the current grammar, compound attack
effects, and live derivation of effect immunity remain separate work.

## Reproduction

Run `python results/physical_attack_energy_disruption_source_bridge/reproduce.py`.

CI workflow:
`validate-physical-attack-energy-disruption-source.yml`.
