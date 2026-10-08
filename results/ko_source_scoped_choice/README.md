# Source-conditioned decision value of Knock Out effect order

## Question

When different currently served official sources identify different players as entitled to order the same Knock Out effect pair, how can a strategy model quantify the resulting disagreement while keeping every source and assumption explicit?

This result composes existing rules-source claims and physical destination outcomes with a **caller-provided** utility function. It computes a source-conditioned choice for each source independently, then reports the utility range across the sourced outcomes.

Implementation: `tools/ko_source_scoped_choice.py`. Reproducer: `results/ko_source_scoped_choice/reproduce.py`.

## Model

Inputs include:

- already-compiled KO destination programs with stable physical instance IDs;
- externally established precedence constraints on effect ordering, if any;
- a timing and exact-interaction context;
- selected official-rules source IDs and concrete player roles;
- a reference player's utility for each destination vector;
- the two opposing players.

`ko_order_outcome_space.ko_order_outcomes` supplies the exact distinct physical endpoints and witness orders. `source_order_chooser.assess_concrete_ordering_player` identifies the chooser under **one** source at a time.

The two-player zero-sum toy model lets the reference player maximize the provided utility if authorized to choose and lets their opponent minimize that utility if authorized. The resulting `SourceChoice` identifies the source ID, chooser, selected endpoint and exact witness order. A source with no applicable claim or missing player context remains unresolved.

Across resolved sources, `payoff_envelope=(minimum, maximum)` records the range of sourced optimal utility values. The envelope is a **range of rule-source-conditioned decisions**, not a probability distribution, confidence interval, or guaranteed win-rate bound for actual tournament play. Every practical utility assignment remains the responsibility of a calibrated gameplay model.

## Concrete Aegislash versus Tyranitar-GX fixture

The immediately preceding source-evidence result [tyranitar_aegislash_authority](../tyranitar_aegislash_authority/) records the official Japanese Q&A for Tyranitar-GX Lost Out versus Aegislash Durable Blade. That source says the Knocked Out Aegislash owner chooses ordering. TPCi's February 2026 Professor guidance instead names the current player for multiple during-turn Knock Out triggers. Their present-day relative authority remains unsettled in this repository.

In a scenario with Tyranitar's player attacking a defender's Aegislash, two already-compiled effect orders produce:

- Durable Blade first: Aegislash plus Honedge and Doublade go to the owner's hand.
- Lost Out first: the full evolution stack enters the Lost Zone.

The fixture defines a **transparent illustrative payoff**: count how many cards from the three-card evolution stack enter the defender's hand. That payoff is 3 when returned and 0 when Lost Out wins.

| Selected source | Authorized chooser | Optimal order under assumed zero-sum payoff | Defender payoff |
| --- | --- | --- | ---: |
| Japan card-specific Aegislash Q&A | defender / KO'd Pokémon owner | Durable Blade first | 3 |
| TPCi Professor February 2026 summary | attacker / current player | Lost Out first | 0 |

The source-conditioned payoff envelope is **[0,3]**, in units of *evolution-stack cards returned to hand*. These are local destination metrics, with no estimated tournament win probabilities.

The result re-authorizes each selected witness through the existing source-aware ordering bridge and then executes both physical outcomes against the full conserved KO ledger. The source policies are never combined into a fictitious consensus chooser.

## Boundary cases and validation

- When the current player and Knocked Out Pokémon owner are the same concrete player, both sources select the same actor. The envelope collapses to **[3,3]**.
- If an externally validated precedence requires Lost Out first, there is only one physical outcome; the envelope becomes **[0,0]** even though the sources still name different choosers.
- Reversing the payoff function reverses the optimal chosen orders. The policy is sensitive to explicit caller preferences and is not hardcoded to favor hand.
- The bundled v3.4 manual's narrower multiple-Pokémon-KO authority case and the unrelated Lost City-specific Japanese Q&A supply no applicable claim for this single-Aegislash interaction.
- Missing player identities and inapplicable sources remain unresolved; malformed inputs and nonfinite utility scores are rejected.

The reproducible regression checks all these cases and verifies that source-chosen orders remain separately legally authorized *within the chosen source profile*, with physical card totals conserved.

## Research implications

This provides a small example of a general uncertainty discipline. A solver can preserve exact consequences even where the governing rule interpretation is disputed. A source-sensitive result can later be resolved by a tournament policy choice without rebuilding the underlying game-state transitions.

The zero-sum objective and the three-card utility are modeling assumptions. In a complete Expanded match, the strategic worth of retrieving Aegislash depends on board position, remaining Prize cards, hand disruption, draw actions, and future win conditions. More sophisticated evaluations should use a real game-state payoff function and validated current regional tournament regulations.
