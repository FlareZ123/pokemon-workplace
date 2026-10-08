# Copied self-healing attacks on the physical actor

## Question

When a copied attack says "Heal N damage from this Pokémon", which physical
Pokemon is healed, and where does that healing sit relative to damage reactions?

## Source contract

The existing conservative healing compiler recognizes complete self-healing
attack bodies of the form `Heal N damage from this Pokémon.`

It currently finds 293 legal attack profiles in the bundled paper-Expanded
snapshot. The profile now preserves its exact attack index, and the parser is
also exposed to the whole-attack coverage inventory.

`tools/physical_attack_healing_source_bridge.py` verifies that the exact
source body event occurred, then applies the healing to the physical Pokemon
that actually executed the copied body. The selected source card supplies the
attack text and does not become the healed board object.

## Card-grounded timing witness

The regression copies Maractus `bw1-11` Mega Drain through Team Rocket's
Persian ex Haughty Order.

The physical copying attacker starts with four damage counters. Mega Drain
deals 20 damage to the opposing Active, heals 20 damage from the copying
attacker during the attack-effect step, and then an attached Spiky Energy
reaction places two damage counters back on the original attacker.

The observed counter sequence is:

`4 before attack -> 2 after healing -> 4 after Spiky Energy`

A second witness copies Elgyem `bw3-54` Calm Mind, which has blank printed
damage and only the exact self-healing text. It heals three counters to zero
without creating a damage record, showing that effect-only copied attacks still
need their source-side effect handler.

## Conservation and identity

Healing mutates only the copying Pokemon's damage counters. The physical card
ledger is unchanged. The source card selected by the copy engine is not
materialized onto the actor board and cannot receive the heal.

## Coverage impact

The whole-attack coverage inventory classifies this family as
`exact_self_healing` with a required `healing` handler. The strict
damage-only materializer continues to reject these attacks.

## Limits

This bridge covers exact self-healing bodies already recognized by the healing
compiler. Full-heal wording, multi-Pokemon healing, healing combined with
movement or other instructions, and conditional healing remain separate work.

Attack eligibility and Energy payment remain upstream. Damage and later
reactions remain owned by their existing physical replay layers.

## Reproduction

Run `python results/physical_attack_healing_source_bridge/reproduce.py`.

CI workflow: `validate-physical-attack-healing-source.yml`.
