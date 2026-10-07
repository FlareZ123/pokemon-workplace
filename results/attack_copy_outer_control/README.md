# Outer control flow for attack-copy effects

## Question

The print-specific copy compiler currently refuses six copy signatures because
they contain conditions outside the selector itself. Are those conditions one
mechanical class?

They separate into declaration eligibility and body-resolution gates.

Implementation: `tools/attack_copy_outer_control.py`  
Regression: `results/attack_copy_outer_control/reproduce.py`

## Rule distinction

The Advanced Player's Rulebook separates announcing an attack from resolving
its instructions. An attack that the Pokémon cannot use cannot be announced.
The same rulebook states that attacks may be used when part of their
instructions cannot be applied, with the applicable instructions followed.

That makes the exact wording around the copy clause mechanically important.

## Current inventory

Across 30 legal copy-attack signatures, six signatures (seven print rows) have
one of the audited outer controls:

- **Nightcap** is a declaration gate: the attack can be used only while the
  opponent has exactly two Prize cards remaining.
- **Skill Thief** is a body gate: the attack remains usable, while the copy
  instruction is reached only when the actor's hand is empty.
- **Assist, Mini-Metronome, Pendulum Influence, and Try to Imitate** are
  stochastic body gates: heads reaches the copy instruction; tails resolves
  without a copied body.

The four coin-gated signatures are represented as requiring an explicit random
outcome rather than silently assuming heads.

## Architectural consequence

A copy executor should preserve at least two condition stages:

1. **declaration eligibility**, checked for the attack actually announced;
2. **body execution gates**, evaluated while resolving attack text.

The existing compiler's single `unsupported_outer_condition` label loses this
distinction and groups Skill Thief with Nightcap even though their conditions
occupy different control-flow stages.

Nested copied bodies make this separation especially important. Exact behavior
for a declaration condition encountered only through another copy effect should
be validated independently before the engine applies declaration-stage logic to
that nested body.

## Validation

The regression scans the legal copy catalog and pins:

- 30 total signatures;
- 6 controlled signatures;
- 7 controlled print rows;
- 4 coin-head body gates;
- 1 exact-Prize declaration gate;
- 1 empty-hand body gate.

It also evaluates both success and failure branches for every control family.

## Limits

This result classifies and evaluates the control conditions but does not yet
mutate the copy kernel. Coin randomness remains caller-supplied, which keeps
stochastic branching explicit rather than burying it in a deterministic state
transition.

The next integration step is to replace the compiler's coarse unsupported flag
with typed declaration/body control metadata and execute the deterministic
branches through the existing copy kernel.
