# From disputed Knock Out ordering to conserved outcome equivalence

**Scope:** paper Pokémon TCG Expanded (Black & White onward), with the repository's current rules-state materialization and Knock Out disposal model. This synthesis links the earlier agent6 and cross-agent Knock Out research to a new exact outcome-space reduction.

## Why ordering is hard

Several mechanisms are easily conflated:

1. **Trigger occurrence and eligibility.** Effects must qualify at their proper attack/checkup/KO phase. Resources consumed before a trigger step cannot simply be recovered afterward. The earlier pre-KO attachment timing result demonstrates this with Energy removed during attack resolution and Huntail's subsequent recovery eligibility.
2. **Ordering authority.** Game rules and card-specific official answers determine who can choose among applicable effects. The existing `effect_order_authority_overlap.py`, `ko_trigger_order_authority.py`, and `ko_redirection_authorized_order.py` separate rules-source provenance from a concrete chooser, and can refuse when sources conflict.
3. **Chosen sequence.** Once an externally legal order is chosen, `knockout_redirection_ordering.py` applies the first explicit destination assignment to each physical card. It deliberately retains explicit discard assignments, which can preempt later hand or Lost Zone redirection.
4. **Destination-only outcome space.** If the currently permitted total orders are available as inputs, `ko_order_outcome_space.py` counts exactly how many produce each per-instance destination vector using a subset dynamic program, including optional externally supplied precedence edges. An output is a count of orders, not a probability of play.
5. **Physical cleanup.** `knockout_zone_routing.py` disposes the frozen KO batch, preserves total card-class counts, dematerializes removed instances, and promotes a surviving Active Pokémon. `ko_order_terminal_projection.py` applies this to every instance-level destination class.
6. **Exchangeable endpoint quotient.** For fixed pending board/promotion and route-only effects, `ko_order_zone_signature.py` gives a complete `(card_class, destination, count)` signature of removed cards. `ko_order_signature_projection.py` groups by this signature before running cleanup once per genuinely different full terminal state.

This layering prevents an algorithm from smuggling in a disputed official ordering rule while still answering carefully bounded questions about physical consequences.

## Evidence and exact outcomes

The original route work is documented in [knockout_redirection_routes](../knockout_redirection_routes/), [knockout_redirection_conflicts](../knockout_redirection_conflicts/), [knockout_redirection_ordering](../knockout_redirection_ordering/) and [ko_redirection_authorized_order](../ko_redirection_authorized_order/).

The new [ko_order_outcome_space](../ko_order_outcome_space/) models an **abstract** trio of already-compiled programs with return, Lost City-like, and selected-Energy-recovery destination geometry. Without precedence requirements there are six total orders and exactly four instance-level endpoints. Their order multiplicities are 2,2,1,1. An external constraint that return must precede both alternative effects leaves one terminal route over two permitted total orders.

The [ko_order_terminal_projection](../ko_order_terminal_projection/) work independently disposes each endpoint through the existing board/ledger kernel, confirming distinct survivor boards and class-zone counts where appropriate. Its synthetic two-Water construction demonstrates that **two distinct instance-level route vectors can yield one identical conserved terminal state**. Once both equivalent Water copies are no longer attached, routing water-1 to hand and water-2 to discard versus the reverse leaves one Water in each zone.

The [ko_order_zone_signature](../ko_order_zone_signature/) result proves a complete histogram invariant for that fixed-board, route-only boundary: every removed instance contributes one count to its gameplay-equivalent card class and destination zone. Equal histograms yield equal full terminal states because the remaining board and unaffected ledger are fixed; unequal histograms yield different class-zone totals. A 220-state deterministic random cross-check tests that equivalence against the existing materialized disposal kernel.

Finally, [ko_order_signature_projection](../ko_order_signature_projection/) uses the histogram to avoid redundant physical disposals. Its 120-case randomized regression compares *all terminal outcome records* against the independent uncompressed projector. On the two-Water example, two instance routes require one physical disposal after signature grouping instead of two.

## Validation ladder

The work uses independent checks at each boundary:

- `results/ko_order_outcome_space/reproduce.py`: 225 randomized exact comparisons against factorial permutation enumeration, plus malformed precedence rejection and 10! to one outcome compression. CI run [37836587469](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37836587469).
- `results/ko_order_terminal_projection/reproduce.py`: previous fixed-order executor, physical card conservation, survivor promotion, and exchangeable endpoint collapse. CI run [37836925772](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37836925772).
- `results/ko_order_zone_signature/reproduce.py`: 220 deterministic randomized full-kernel signature equivalence witnesses. CI run [37837191137](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37837191137).
- `results/ko_order_signature_projection/reproduce.py`: 120 randomized comparisons to uncompressed physical cleanup. CI run [37837359878](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37837359878).

## Strategic and modeling consequence

A game-state optimizer should distinguish three different kinds of apparent branching: alternative effect orders, different physical-instance destinations, and strategically distinguishable terminal states. The second and third can be dramatically smaller than the first. For this narrow destination-only KO model, exact compression preserves possible physical endpoints and every order count.

The resulting counts should **never** be interpreted as equiprobable choices by real players. When a player chooses an order strategically, their policy depends on board context, Prize positions, matchup, and payoffs. Unknown or disputed authority likewise cannot be replaced by uniform random order selection.

## Unresolved boundaries

- Real effect co-activation and timing, especially triggered effects that change the resources required by later triggers.
- Resolving differences among official ordering-source versions and regions; a named chooser is still required whenever outcome depends on the choice.
- Extending histogram equivalence to effects that mutate or inspect survivors, Energy attachments outside the KO batch, ability suppression, draw/order information, or card-instance history.
- Converting route endpoints into adversarial or policy-weighted payoff values, with win/Prize effects and the one-Supporter-per-turn constraint where relevant.
- Measuring complexity and physical executor savings on real legal decks and reachable board states rather than synthetic route maps.

This synthesis makes no claim that every combination of abstract route programs occurs together in real Pokémon play. It preserves exact conditional results and identifies the rules-verified layers still needed for faithful strategic simulation.


## Source-conditioned chooser decisions and invariance

Two new layers address why an unresolved authority claim matters strategically:

- [tyranitar_aegislash_authority](../tyranitar_aegislash_authority/) validates a directly sourced Japan card-specific Q&A: Aegislash's owner chooses the order of Durable Blade and Tyranitar-GX Lost Out. The physical return-first versus Lost Out-first outcomes for the full Aegislash evolution stack are verified. The source is kept separate from TPCi's February 2026 current-turn-player guidance.
- [ko_source_scoped_choice](../ko_source_scoped_choice/) evaluates the source-conditioned optimum under an explicit zero-sum two-player utility. For a transparent utility that counts Aegislash, Doublade and Honedge returned to the defender's hand, the Japan-profile defender selects the three-card return and the TPCi-profile attacking current player selects zero-card recovery. The **[0,3]** interval is a conditional unit-count value envelope, with no assigned source probability.
- [ko_choice_invariance](../ko_choice_invariance/) retains all tied-optimal outcomes and distinguishes invariant utility, invariant physical-instance destination vector and invariant conserved terminal state. A tied utility may leave physically distinct outcomes; two instance-level water-energy routes may differ while producing identical terminal exchangeable counts. The regressions validate 110 random cases against the full physical KO executor.

These studies reinforce an evidence boundary. Source authority, caller utility and physical state equivalence are independent inputs. Reliable optimization can identify uncertainty-neutral choices without inventing which presently served official rules source governs a particular tournament.
