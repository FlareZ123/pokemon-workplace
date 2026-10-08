# Source-conditioned Knock Out decision over conserved terminal states

## Why a state-based payoff matters

A payoff evaluator should usually value the game state a player will actually receive after the Knock Out. Different physical-instance routing histories may lead to an identical exchangeable state once cards are returned to hand, discarded, or sent to Lost Zone.

Earlier source-scoped optimization enumerated every instance destination vector before scoring it. For many identical Energy cards, that can make an apparently modest decision problem computationally enormous.

`tools/ko_source_terminal_choice.py` combines the new [exact terminal histogram convolution](../ko_order_histogram_convolution/) with the established official-rules source-chooser layer. It computes each source's zero-sum optimal choices directly over conserved `StackBoardMaterialState` outcomes. It preserves every state tied for the optimum and never silently merges conflicting authority sources.

## Inputs and outputs

Inputs are a frozen pending-KO batch, compiled destination programs, an optional externally validated precedence relation, source IDs and timing context, concrete player roles, a selected viewpoint player and opponent, and a payoff function of the **complete terminal state**.

For every source, the result includes:

- applicable ordering authority status and concrete chooser if resolved;
- one optimal terminal state and its executable witness order;
- all equally valued terminal states;
- viewpoint payoff under the assumed zero-sum chooser preferences.

A payoff envelope across source-conditioned optima records how much the chosen result depends on source authority. Unresolved sources remain explicitly unresolved. Labeled effect-order multiplicities stay available in the convolution output, but are never treated as player choice probabilities.

## Official card-specific witness

Japanese official Q&A on Aegislash's Durable Blade against Tyranitar-GX Lost Out allows Aegislash's owner to choose effect order, while February 2026 TPCi Professor guidance assigns multiple during-turn KO effect ordering to the current player. Their source-specific roles can differ for a defending Aegislash.

Define the defending player's utility as the **number of Honedge, Doublade and Aegislash evolution cards returned to hand**.

- Under the Japan Q&A profile the defender selects Durable Blade first, recovering all three cards, payoff 3.
- Under the TPCi current-player profile the attacking player selects Lost Out first, sending those cards to the Lost Zone, payoff 0.

The source-conditioned envelope is `[0,3]` in returned-stack-card units. An equal-value utility preserves both physically different states as tied optima. This remains a transparent toy utility, with no claim to estimate match win rate.

The test independently compares every selected terminal state with disposal of the old instance-based source solver's chosen order and verifies complete conservation.

## 80-effect synthetic scalability witness

With 40 equivalent Basic Water Energy attached to a KO'd Lapras and 80 abstract competing destination effects, `2^40` different instance-route vectors collapse to 41 final exchangeable terminal states.

A full-state utility defined as the number of Basic Water Energy returned to the player's hand has an unambiguous optimum at either endpoint:

- If the defender controls the order and maximizes the payoff, the optimum returns 40 Water.
- If the attacker controls it and minimizes the defender's payoff, the optimum returns 0 Water.

Each case examines 80 component-local outcomes and 41 conserved terminal states. Exact total order multiplicity remains `80!`, but no trillion-element instance-route enumeration occurs.

The 80-effect fixture is synthetic. It tests a mathematically valid optimization implementation, without asserting a real card combination yields those simultaneous effects or source authority.

## Reproduction

`python results/ko_source_terminal_choice/reproduce.py` checks the concrete Aegislash ruling, unchanged physical card totals, strict and tied source-conditioned optima, unresolved sources, **120 deterministic randomized comparisons against the original instance-level source solver**, and the 40-Water scalability fixture.

The companion GitHub Actions workflow is `validate-ko-source-terminal-choice.yml`.

## Limitations

The new solver models only static destination-only KO effects from one frozen batch and fixed promotion. A complete tactical utility should incorporate Prize cards, following-turn interactions, hand/deck uncertainty and opponent responses. Real triggered effects, legality, and tournament rules source precedence remain external to the compiled route model. The retained exact outcome counts are mathematical cardinalities of labeled orders, not empirical action frequencies.
