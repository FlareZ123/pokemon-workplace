# Attack-copy execution phases and source lifetime

## Question

Can an Expanded attack-copy resolver safely treat the phrase `use it as this attack` as a simple tail call, with surrounding card text executed strictly in printed order?

No. The current legal card pool contains several distinct execution shapes that require explicit phases.

Implementation: `tools/attack_copy_execution_phases.py`  
Regression: `results/attack_copy_execution_phases/reproduce.py`

## Rules basis

Advanced Player's Rulebook section C-18 defines `use it as this attack` as choosing an attack and doing all of its effects and damage. It also states that the copied attack normally ignores its printed Energy cost unless the copying text says otherwise.

The same section gives Ditto's **Copy Anything** as the explicit exception:

`Choose 1 of your opponent's Pokémon's attacks and use it as this attack. If this Pokémon doesn't have the necessary Energy to use that attack, this attack does nothing.`

This is important for execution order. Although the Energy condition is printed after the copy phrase, it must gate whether the copied body happens at all. The rulebook's treatment therefore shows that lexical clause order is not sufficient to infer semantic execution order.

## Card-pool inventory

The deterministic scan uses the repository's current effectively legal paper Expanded snapshot and the same seven-print ban overlay used by the existing legality tooling.

It finds:

- **14,836** effectively legal card prints scanned;
- **64** print-level attacks containing `as this attack`;
- **30** distinct attack-name/text signatures.

Among those 30 signatures, trailing text after the copy phrase classifies as:

| Trailing semantics | Signatures |
| --- | ---: |
| none | 26 |
| selected-attack Energy gate | 1 |
| GX-use rule | 1 |
| true post-copy cleanup | 1 |
| explanatory reminder | 1 |

There are no currently unclassified trailing forms in the snapshot.

## Clause position is not execution order

Two legal attacks express selected-attack Energy gating on opposite sides of the copy phrase:

- Kecleon `bw9-94`, **Imittack**: the Energy condition is printed before `use it as this attack`.
- Ditto `det1-17`, **Copy Anything**: the Energy failure condition is printed after `use it as this attack`.

A compiler that executes copied effects immediately when it encounters the copy phrase would get Copy Anything wrong. The selected attack must first be known, then its copied-use gate must be evaluated, and only then may its body execute.

This suggests a semantic normalization step such as:

`select target -> evaluate selected-target-dependent gates -> execute copied body`

rather than direct left-to-right execution of text fragments.

## The selected source may leave its lookup zone before the body executes

Two signatures expose a separate lifetime problem.

### Hypnotic Reign

Malamar `sm10-119` reveals the opponent's hand, may discard a Pokémon found there, then uses one of that discarded Pokémon's non-GX attacks as the copying attack.

The source Pokémon is no longer in the opponent's hand when the selected attack body executes.

### Seek Inspiration

Slowking `sv7-58` discards the top card of the user's deck. If that card is an eligible Pokémon, it chooses one of that card's attacks and uses it as the copying attack.

The source Pokémon is already in the discard pile when its attack body executes.

These cards show that a resolver should snapshot the chosen attack definition at selection time. It should not preserve only a live query such as "an eligible attack from the opponent's hand" and re-run that query immediately before nested execution.

A stronger phase model is:

`discover source -> select attack -> commit required source movement -> execute snapshotted attack body`

The selected attack body's semantics survive the source card leaving the zone that originally made it discoverable.

## True continuation after the copied body

Team Rocket's Persian ex `sv10-150` / `sv10-219`, **Haughty Order**, has a genuine continuation:

`reveal top 10 -> optionally execute selected attack body -> shuffle revealed cards back`

The shuffle belongs after the copied body. This validates the execution-frame approach already introduced in `results/attack_copy_semantics/`: copied bodies can return control to the outer attack.

## Trailing text can also be a rule rather than a continuation

Zoroark-GX **Trickster-GX** places the once-per-game GX restriction after the copy phrase. That footer is a use constraint on the outer GX attack, not ordinary cleanup to be scheduled after the copied body.

Slowking **Seek Inspiration** places the Rule Box reminder after the copy phrase. That parenthetical explains the preceding eligibility condition and does not represent an executable continuation.

So a parser needs semantic roles, not only prefix/suffix positions.

## Simulator implication

A robust copy resolver needs at least these conceptual phases:

1. establish any outer attack prerequisites and stochastic branches;
2. discover candidate source objects;
3. select an attack and snapshot its executable definition;
4. apply selected-target-dependent legality checks;
5. perform any source-zone mutation required by the outer attack;
6. execute the selected attack body as a nested frame;
7. resume genuine outer post-copy continuation;
8. finish the declared attack and only then cross the turn boundary.

This phase model complements the existing findings on declared attack identity, edge-local restrictions, copy-stack recursion, source-variable correlation, and outer-text resumption.

## Limitations

The classifier is intentionally conservative and wording-specific. It describes all 30 copy-attack signatures in the current bundled snapshot, but new card wording may introduce additional semantic classes.

The source-lifetime detector currently recognizes the two concrete discard-before-body families in the snapshot. It is evidence for the architectural requirement, not a complete natural-language compiler.

The result does not attempt to resolve every copied attack's damage, state mutation, or strategic value. Its target is execution structure.
