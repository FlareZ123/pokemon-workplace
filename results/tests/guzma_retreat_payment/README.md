# Guzma's forced pivot and physical Retreat payment

**Exact one-turn rules-mechanics study.** This is a controlled witness, not a measured match win rate or a replacement recommendation.

## Rules and tactical situation

Guzma (sm3-115) gusts an opposing Benched Pokémon and, if successful, must switch your own Active with your Bench. Boss's Orders (swsh2-154) gusts without that own switch. A normal Retreat may occur once per turn and discards whole attached Energy cards to pay its cost (Advanced Player's Rulebook A-03/C-01). A Switch Item can reposition the player without payment, if Items can be played.

Opponent: a one-Prize Active and a three-Prize Bench target. Our Active can KO the Benched target if it retains one Colorless-compatible Energy unit and has Retreat Cost 1. Our only Bench Pokémon cannot KO the target, has Retreat Cost 2, and has no Energy.

| Our Active's attached Energy | Boss immediate Prizes | Guzma immediate Prizes |
| --- | ---: | ---: |
| One Double Colorless Energy card (2 units) | 3 | **0** |
| Two Basic Energy cards (1 + 1 units) | 3 | **3** |
| One Basic Energy | 3 | **0** |

Guzma can preserve the first attacker by Retreating it **before** playing Guzma, then promoting it back with Guzma's own switch. When Retreat consumes one Double Colorless Energy card, all two provided units disappear and the attacker cannot pay its attack cost. With two Basic Energy cards, the player discards one and retains one, enabling the three-Prize KO. A Guzma-first attempt cannot restore the original attacker because the newly promoted unpowered Bench Pokémon has Retreat Cost 2.

Changing the own Bench's Retreat Cost to zero permits **Guzma first, then free Retreat** back to the original attacker, even with Double Colorless attached. If a Switch Item is held and playable, both sources can reach the same attacker without discarding Energy. Item lock removes that option, though payable normal Retreat remains possible.

## Methods and reproducibility

tools/guzma_retreat_payment.py composes the earlier [source-comparison frontier](../guzma_forced_pivot_frontier/) with the existing physical payment helper in tools/typed_retreat_gust.py. It models a fixed opposing Active/Bench pair; own Pokémon carry target-KO eligibility bits, Colorless-compatible attack costs, Retreat Costs, and whole physical Energy cards, plus possible retreat prohibition. It explores orderings of one paid Retreat, one optional held Switch Item, one held targeted Supporter and one final attack.

The independent reproducer uses breadth-first enumeration of physical actions, checking **3,654** scenarios against the production recursive search and **6,048** reductions to the earlier mask-only model. It verifies sm1-136 Double Colorless Energy, sm3-115 Guzma and swsh2-154 Boss printed text; explicit Energy configurations, Item-lock ablations and free-retreat cases are asserted.

Run from repository root: python -m results.tests.guzma_retreat_payment.reproduce

**Limits:** The model supplies immediate KO eligibility externally, handles all Energy as Colorless-compatible, and omits real attack damage, Pokémon typing, evolving, damage persistence, opponent decisions and future turns. The examples are **synthetic card-mechanics witnesses**, not asserted positions reached by the champion Shadow Rider or Aichi Mew lists. Before considering a real tournament Guzma/Boss swap, integrate specific attack costs, Energy types, existing attached cards, Tools, and lock-state transitions.
