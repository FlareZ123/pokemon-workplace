# Regidrago copied Dragon Impact: response-aware reattachment

**Evidence:** Exact rules-grounded 48-cell attack-readiness calculation with an independent physical Energy-unit matching oracle. Hypothetical probability examples are not empirical deck or match results.

## Printed physical fixture

Regidrago VSTAR (swsh12-136) uses its Grass/Grass/Fire Apex Dragon to copy Salamence ex (sv9-114) Dragon Impact for 300 damage. The attack instructs it to discard two Energy. It starts with one Double Dragon Energy (xy6-97, two typed Energy units on a Dragon), one Basic Grass and two Basic Fire. The four irredundant payments are DDE alone, Grass and one Fire, or both Fire. The source-verified base enumerator is tools/energy_discard_continuation_frontier.py.

After this attack, suppose Regidrago survives a single opposing response: no counter, Enhanced Hammer (sv6-148), or Temple of Sinnoh (swsh10-155). On the next player turn, it may manually attach one Energy from hand, categorized as none, Grass, Fire or new DDE. We check only if Apex Dragon's Grass/Grass/Fire cost is payable. The payment is chosen *before* the opponent response and the future hand category are known.

## Exact results

| Energy discarded | Opponent response | No Energy | Grass | Fire | DDE |
| --- | --- | --- | --- | --- | --- |
| DDE (one card) | None | No | Yes | No | Yes |
| DDE | Enhanced Hammer | No | Yes | No | Yes |
| DDE | Temple | No | Yes | No | No |
| Two Basics (three payment pairs) | None | Yes | Yes | Yes | Yes |
| Two Basics | Enhanced Hammer | No | No | No | Yes |
| Two Basics | Temple | No | No | No | No |

Enhanced Hammer has no Special Energy target on the modeled attacker after DDE was discarded. After Temple, attached new DDE provides one Colorless unit rather than two flexible typed units. This table is 4 actual payments × 3 responses × 4 hand states = **48 validated cells**, collapsed by identical Basic-pair outcomes.

Thus a known next-turn Grass attachment gives the DDE-discard choice a protection advantage against the two counters. Without those counters, retaining DDE is ready immediately and preserves the manual attachment for other uses. The result does not value the discarded DDE, other Pokémon, or the alternative uses of that attachment.

## Conditional precommitment calculation

Let h and t denote opponent Hammer and Temple probabilities, g and d the probabilities that the next hand Energy is Grass or DDE. The response and hand categories are exclusive within each group and **assumed independent only in this toy model**.

- P(next-Apex-ready | discard DDE) = g + (1-t)d
- P(next-Apex-ready | retain DDE) = (1-h-t) + hd
- Indifference, provided d is less than one: h = ((1-t)(1-d)-g)/(1-d)

Illustrative priors: hand (none, Grass, Fire, DDE) = (3/10, 1/2, 1/10, 1/10), Temple = 1/10. The crossover Hammer probability is **31/90**. At Hammer = 3/5, discard DDE gives **59/100** readiness, retain DDE **9/25**. At Hammer = 1/10, discard DDE gives **59/100**, retain DDE **81/100**. These numbers are mathematical consequences of synthetic priors and should never be cited as realistic matchup frequencies.

## Reproduce and interpret

Run `python -m results.tests.energy_discard_response_reattachment.reproduce` from repository root. It invokes tools/energy_discard_response_reattachment.py, compares every cell against an independent physical-slot backtracker, and evaluates 66 exact probability-lattice cases. The implementation uses existing official-print checks and the shared attack-cost and opponent-response functions.

The 2025 official Expanded Regidrago example included Salamence ex and DDE: https://www.pokemon.com/uk/features/a-deep-dive-into-the-2025-pokemon-tcg-expanded-format . The published Aichi 2026 tenth-place Regidrago deck in this repository **does not include Salamence ex**. This test does not recommend an Aichi deck swap. It omits actual hand and Prize distributions, counter access and timing, attacker survival, alternative Stadiums, VSTAR Power recovery, and full match outcomes.
