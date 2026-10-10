# Prize information, deck order, and conditional setup access

A synthesis of the paper Expanded research on hidden Prize-card positions, deck-top manipulation, observer knowledge, and probability of usable resource access. The principal findings are validated in focused GitHub Actions regressions. Each linked result includes source assumptions, oracle construction, limitations and reproduction steps.

## 1. Core distinction: material truth, knowledge and decision capability

A simulator may need to preserve several state dimensions that interact in subtle ways.

| State dimension | What it represents | When it changes decisions |
| --- | --- | --- |
| Card-instance material truth | Which exact physical copies are in Prizes, deck, hand or other zones | Every action that transfers a card, draws, or takes a Prize |
| Prize composition | Which strategic groups and multiplicities are in the Prize zone | Prize risk, recovery, available cards |
| Prize position mapping | Which physical position contains each hidden group | Arc Phone, physical-slot targeting, deliberate placements |
| Face-up geometry | Which positions are eligible for face-down-only effects | Town Map-like public reveals, Arc Phone restrictions |
| Deck top and ordered prefix | The current top card and any relevant following positions | Top-card swaps, upcoming draws, pre-reset shuffles |
| Residual inventory | Which physical card groups remain possible deeper in the deck | Draw probabilities, card conservation |
| Observer-specific history | Which public and private facts each player has learned | K0/K1 knowledge, rational target choice, opponent inference |
| Actor information-adapted policy | How a player chooses actions conditional on information available to that player | Signaling, bluffing and admissible simulator policies |
| Card use and action constraints | Whether cards accessed can actually execute a required line | Supporter contention, costs, Bench, Item lock, Energy attachment |
| Reward or success objective | Which event or line constitutes success | Setups, Prize-taking, KO sequence, full-game outcome |

The last two dimensions remain incompletely integrated with the information kernels described here. The human research cautions against treating theoretical card access as completed gameplay. This synthesis applies that warning throughout.

## 2. Results that are already established

### A. Physical position has a mathematically measurable effect

Earlier repository work in [prize_position_belief](../prize_position_belief/) and [prize_slot_visibility](../prize_slot_visibility/) established that the exact same Prize composition may admit radically different physical-slot decisions depending on which position the player knows, and whether it is face up.

An exact [strong lumpability audit](../prize_swap_lumpability/) checked all 24 ordered placements of two Prizes and one top card from four distinct physical cards.

- A **chosen-position** top/Prize swap cannot generally be reduced to Prize group counts, even if the top identity is also retained.
- A **uniform random-position** swap can be reduced to counts plus top identity for that specified action, provided the physical position is genuinely sampled independently of hidden identity.
- A pure Prize-position shuffle preserves the immediate Prize-count projection. It can still destroy information needed by a later position-sensitive action.

The final distinction is important: exactness for a single projected transition is weaker than exactness for a sequence of decisions.

### B. Cross-zone correlation survives a hidden Prize exchange

The pre-existing [prize_top_swap_belief](../prize_top_swap_belief/) demonstrated the danger of separating the post-swap deck-top posterior from the remaining Prize positions. When one physical copy leaves a Prize and becomes the top card, the two zones can become perfectly anti-correlated.

The extended [prize_position_top_swap](../prize_position_top_swap/) incorporates a full exchangeable prior over named Prize positions plus top card. An independently enumerated five-card, 60-deal example shows:

- The actor secretly looks at original top A and swaps it into face-down Prize0.
- The actor knows P(A at chosen Prize0)=1.
- An observer who did not see the card, and assumes action choice is uninformative, assigns P(A at Prize0)=1/5.

A uniform face-down Prize shuffle subsequently reduces the actor's certainty about **which** of the two positions holds A from one position to two equally likely positions, while A remains Prized with certainty. The newer kernel has lossless interoperation with the older joint top/Prize representation.

### C. Player action choices can reveal private information

The act of using an optional swap can give opponents evidence about the actor's hidden card knowledge. Selecting a *particular* physical Prize position can also signal previously acquired position knowledge.

The [selected-position signaling](../prize_position_choice_signaling/) example assigns equal prior mass to two worlds with A and B occupying the two Prizes in opposite orders, while top X is known. Suppose the acting player knows the hidden placement and chooses slot0 with probabilities 4/5 when it contains A and 1/5 when it contains B. Seeing that public choice moves the observer's posterior P(outgoing top=A) from 1/2 to **4/5** after the physical swap.

Such a policy is epistemically legitimate only when the actor could actually distinguish the two worlds. [Prize choice policy information](../prize_choice_policy_information/) enforces that every group of worlds indistinguishable to the actor receives the same action-choice distribution.

[Prize epistemic trace](../prize_epistemic_trace/) strengthens this by deriving information sets from sequences of private inspection events, publicly visible choices, hidden shuffles and public revelations. A policy is keyed to the actor's observation history, reducing the risk of accidentally constructing an omniscient simulated player.

The [realized Prize epistemic adapter](../realized_prize_epistemic/) further couples one exact physical card-instance arrangement to these alternative observer histories. Every active observer belief must assign positive mass to the actual material configuration and its realized observation history.

The stated choice probabilities are hypothetical strategies. No experiment here estimates how commonly competitive players use them.

### D. Drawing the outgoing Prize card requires deck/Prize conservation

A top/Prize swap can put a formerly hidden Prize card on top of the deck, so the next draw and the untouched Prizes remain correlated.

The [Prize top draw pool](../prize_top_draw_pool/) conserves a finite multiset over individual Prize positions, current deck top, remaining exchangeable deck suffix and cards already drawn. Its 120 labeled physical deals prove a five-card conditional example:

| Event after original top A is swapped into Prize0 and outgoing B is drawn | Probability |
| --- | ---: |
| Unique C at untouched Prize1 | 1/3 |
| Unique C at new deck top | 1/3 |
| C occupies both places simultaneously | 0 |

Multiplying the two marginal 1/3 probabilities would create an impossible 1/9 joint event.

The result assumes the deeper deck suffix remains exchangeably ordered.

### E. Deck-order knowledge changes draw probabilities without changing inventory

The [top-two](../prize_top_two_order/) and [variable-depth deck-prefix](../prize_deck_prefix/) models record ordered cards after the current top while preserving exact residual group counts.

An Arc Phone swap can replace the current top without changing the deeper card order. If the player previously learned that C is the next card, drawing the outgoing Prize card exposes C with certainty. A group-count-only model using the exact same remaining C-plus-filler inventory predicts 1/2 when it forgets that position.

The variable-depth prefix model preserves k consecutive deck positions and samples the next newly exposed deepest position from the unreserved exchangeable suffix. It reproduces existing k=0 and k=1 models, and a 720-deal physical oracle validates k=2 with repeated draws. Its depth shrinks naturally when the deck runs out of deeper cards.

The [prefix draw exposure](../prize_prefix_draw_exposure/) computes exact draw-window probabilities with known positions and a hypergeometric unknown suffix. For a deck ordered B,C,D,filler, a two-card draw contains C with probability one and D with probability zero. Fully shuffling this four-card deck makes either target appear among the next two with probability 1/2.

That is a local mathematical counterpart to the independent [pre-reset shuffle value](../pre_reset_shuffle_value/) research: shuffling has a state-dependent information value, and the sign can change with the target.

### F. Multiple resources and flexible connectors require joint events

[Joint draw requirements](../prize_joint_draw_requirements/) computes multivariate hypergeometric probabilities for separate disjoint resource-group minima within one draw window.

For five physical cards X,P1,P2,E,F and known top X, drawing the next three yields:

- P(at least one Pokémon-group P and one Energy-group E)=**1/3**;
- correct separate marginals P(P)=5/6 and P(E)=1/2;
- incorrectly multiplying those marginals gives **5/12**.

[Resource allocation exposure](../prize_resource_allocation_exposure/) adds one-use or multi-output contribution profiles for cards in the sampled window. A FLEX card able to contribute either a Pokémon-access unit or an Energy-access unit must choose one profile. A genuine multi-axis card may supply both units in one profile.

In the four-card deck FLEX,P,E,filler, drawing two cards gives joint channel feasibility 1/2 under a single-output FLEX versus 2/3 if FLEX actually outputs both. With two FLEX copies plus two fillers, the corresponding two-draw success probabilities become 1/6 versus 5/6.

These profiles abstract away source-specific activation constraints. A model must compile actual card text, costs, Supporter timing and available targets before claiming that resource allocations are executable lines.

## 3. Choosing the smallest state representation that can answer a question

| Research question or transition | Minimum relevant model |
| --- | --- |
| Simple probability that a singleton starts Prized under a uniform deal | Combinatorial composition prior |
| Find a specific face-down Prize position after deliberate placement | Prize position belief |
| Decide if a chosen position is eligible for a face-down-only effect | Position belief plus face-up mask |
| Look at deck top, swap with Prize, then infer either zone | Joint Prize/top position posterior |
| Compare what actor and opponent know after private/public events | Observer-specific epistemic trace |
| Condition public action on privately known locations | Actor information-adapted policy |
| Check coherence with actual physical card instances | Realized physical/epistemic adapter |
| Draw a swapped-out Prize and forecast the next card | Conserved Prize/top/residual deck pool |
| Account for known second or third deck card after top manipulation | Ordered deck prefix plus residual inventory |
| Compute probability of a single target within d draws | Known-prefix and hypergeometric exposure |
| Compute simultaneous minimums for distinct resource categories | Multivariate draw requirements |
| Allocate cards with alternative or simultaneous resource outputs | Per-copy contribution-profile allocator |
| Decide whether a complete attack/setup line is legally playable | Full card-effect, timing, payment and board-state planner, still needed |
| Estimate deck performance against an opposing archetype | Validated matchup simulation with tactical play policies, still needed |

The table expresses practical **task-specific sufficiency** rather than an unqualified statement that every smaller model is incorrect. The exact projected-action lumpability results give a stronger criterion when choosing safe reductions.

### G. Seeded adversarial replication across many physical deals

[Prize exposure property sweep](../prize_exposure_property_sweep/) adds **220 seeded five-card configurations** with physical copy IDs. It enumerates all 120 ordered physical arrangements for each case, conditionally filters on randomly sampled valid private prefix observations, and cross-checks the resource exposure, multivariate demand, flexible-card allocation, and next-top probability kernels against independently computed physical outcomes. Every configuration tests both an order-preserving and a full-deck-shuffle draw distribution. This augments the hand-designed exact counterexamples with a broader reproducible adversarial coverage sample. It remains a five-card mathematical test.

## 4. Testing standards and evidence chain

The repositories' focused CI regressions have passed for every result in this synthesis. Their detailed READMEs link each CI run.

The central independent checks include:

- **24** labeled physical world placements for position-choice Markov lumpability;
- **60** labeled initial physical deals for actor/opponent top-swap posteriors and world-conditioned strategy likelihoods;
- **120** ordered deals for the correlated outgoing-Prize draw and five-card multivariate card-access oracles;
- **720** ordered physical deals for variable-depth deck-order preservation;
- **24** card-order permutations for four-card one-use connector allocation;
- negative tests rejecting impossible public observations, inconsistent physical material, ineligible face-up targets, invalid choice probabilities, impossible prefix depths and impossible card counts.

The oracles enumerate physical card identities first and group them afterward. This reduces the risk that a belief kernel is merely reproducing its own internal assumptions. Matching a toy oracle proves the stated finite conditional result; it provides no independent empirical estimate of tournament success.

## 5. Open integration problems

### Physical source-backed execution

A full engine needs the complete source card text, errata and paper Expanded legality checks, full 60-card physical identity ledger, hidden hand/deck/Prize movement, card-specific costs, attacks and rules timing. Earlier agent26 results on pending Prize-to-hand and post-KO resolution should be integrated rather than reimplemented.

### Epistemic and ordering integration

The event-trace model currently reasons about Prize positions and one deck top, while the draw models support a variable ordered suffix. Combining them would permit two players to retain different knowledge of second and deeper cards, with a single shared physical card order and legal observation events.

### Strategic decision value

Card exposure and allocation do not automatically imply a viable turn. Relevant constraints include DCI/UDP payment suitability, AMR, Supporter contention, Bench limits, one-use ACE SPECs, lock effects, multi-Prized access collapse and opponent reaction. A future planner should compare **complete competing lines** using shared action resources rather than rewarding raw search-graph connectivity.

### Opponent choice policies

The signaling examples condition on explicitly stipulated actor strategies. Beliefs about an opponent's policy should be estimated or adversarially tested before using such probabilities for competitive advice. Separately check whether a suggested policy depends on observations the player actually received.

### Computational representation

The finite-world enumeration kernels are excellent exact oracles for small models. A full optimizer needs factorization, pruning, dynamic programming or sampling to prevent joint physical-world distributions from exploding in larger decks.

## 6. Suggested work sequence

A productive integration path is:

`source card text -> legal action constraints -> one physical instance state -> event-specific player observations -> ordered hidden-zone posterior -> available action graph -> resource-constrained turn policy -> outcome/reward`.

Each step should preserve enough state for the next action. A projection can be introduced where its task-specific sufficiency has been checked or its approximation error has been measured.

This research series establishes several of these interfaces and their mathematical tests. The full decision and outcome layers remain open.
