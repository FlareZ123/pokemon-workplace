# Sequential public random discards can erase earlier Prize-origin evidence

## Question

Can two observed random hand discards restore uncertainty about a previously Prized hidden card that was changed by the first observation?

Yes. The key is that card draws from a shrinking hand occur **without replacement** and that surviving hand composition depends on whether an earlier card was the exact Prize-origin copy.

Implementation: `tools/prize_acquired_random_discard_chain.py`  
Regression: `results/prize_acquired_random_discard_chain/reproduce.py`

## Context and exact oracle

A player previously declined an optional Chansey Prize trigger, leaving a three-card hand with one tagged Prize-origin card of uncertain group C or O and two otherwise known cards, one C and one O. The observer's initial posterior after decline is P(tag C)=2/7 and P(top S)=13/35. A relevant Expanded-legal source of random hand discards is **Mars** (`sm5-128`, Ultra Prism), which draws two cards and, if successful, discards one random opponent-hand card. Consecutive random discards may come from different qualified effects; this model does not claim one Mars card supplies both.

The oracle enumerates every ordered pair of distinct physical indices from the three-card hand. Each ordered pair has probability 1/6 conditioned on the hidden world. It then conditions on the public card groups observed in the order of discard, and retains the hidden fact of whether the tagged physical instance survived.

| Public ordered discards | P(tag C) | P(top S) | P(tag still in hand) |
| --- | --- | --- | --- |
| C then C | 1 | 4/5 | 0 |
| C then O | 2/7 | 13/35 | 1/2 |
| O then C | 2/7 | 13/35 | 1/2 |
| O then O | 0 | 1/5 | 0 |

**Surprising cancellation:** a public C then O sequence has probability 1/3 conditional on either hidden tagged class. Its likelihood ratio is therefore one. The second public discard cancels the evidentiary effect of the first and returns the opponent's beliefs about the originally Prized card and deck top to their pre-discard values. The same occurs for O then C. In contrast, two C observations imply the tagged card was C, and both C copies have left the hand.

## Physical state and observer asymmetry

The tested physical world has the tagged card actually C. Six exact sequences are checked: all legal ordered selections of two of the three cards. The test includes cases where the tagged Prize itself leaves and cases where only other copies leave.

Each posterior world tracks (deck top, remaining Prize composition, tagged group, whether tagged remains in hand, residual non-tagged hand counts). After each discard, the actor's belief is conditioned on its observed **exact-origin event**; the opponent conditions only on the publicly discarded group.

The result preserves materialized card identity and per-class conservation throughout both discards, and refuses to continue with a card that is no longer in the hand.

## Scope

The result is exact for the controlled four-world prior, known composition of the two other hand cards, uniform hand sampling, and no additional hidden actions between discards. It does not independently prove these assumptions reflect typical tournament play or model the Trainer legality and preceding draw effect of Mars. Unknown other-hand composition, multiple identical print classes and longer sequences require further care.

The general strategic consequence is that separate Bayesian updates using a fixed initial hand composition are wrong for sequential random discards. The correct conditional next-card distribution must depend on which card copy may have left in each still-possible hidden world.
