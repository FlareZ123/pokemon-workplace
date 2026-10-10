# Turn-indexed Item permission exposes off-window defensive value

## Question

A static Item lock flag suppresses Switch during all opposing turns. How does a more realistic sequence of allowed and disallowed Item turns change the value of a defender's Switch in the [Boss–Switch critical-window endgame](../gust_switch_critical_window/)?

The new [exact chance/minimax implementation](../../tools/timed_item_lock_gust.py) associates Item permission with **the defender's own actual turn number**. The Item mask is exogenous: it represents the resolved effect of an unspecified lock, and it does not simulate the source Pokémon, Stadium or attack that applied the lock.

## Constructed endgame

The defender starts with an Active Pokémon worth three Prizes and requiring two hits, and Benched two-Prize and three-Prize Pokémon that also require two hits each. The attacker needs six Prizes. Each player has its own 12-card hidden random draw pile; the attacker has one Boss's Orders and eleven inert cards, the defender one Switch Item and eleven inert cards. Attacks deal one persistent durability hit to the Active; there is no other retreat, Item, Supporter or search effect, and defender promotion after KO remains adversarial.

At the start of each defender turn it draws once. It can play Switch that turn if Item permission for that specific turn is true, retaining an unused Switch drawn on a locked turn. The attacker can use Boss if drawn. Both optimize the number of attacker attack turns under the chance/minimax model.

Each of the first five defender turns can independently be permitted or blocked in the model. A mask bit `1` means Item play allowed that turn, `0` blocked; later turns are allowed but irrelevant for this board. There are `2^5 = 32` masks.

## Eight distinct chance/minimax values

The exact solver shows that permission on defender turns **2 and 5 changes nothing** in this fixture. The 32 masks collapse to eight distinct states determined by defender-turn permissions `(t1,t3,t4)`:

| Allowed turns among 1, 3, 4 | Expected attacker turns |
| --- | ---: |
| None | `65/12` = 5.416667 |
| 4 only | `49/9` = 5.444444 |
| 3 only | `11/2` = 5.5 |
| 3 and 4 | `401/72` = 5.569444 |
| 1 only | `787/144` = 5.465278 |
| 1 and 4 | `395/72` = 5.486111 |
| 1 and 3 | `199/36` = 5.527778 |
| 1, 3 and 4 | `401/72` = 5.569444 |

With Items locked on all five turns, Switch cannot interfere and the outcome coincides with the source-free `item_legal=False` engine. With all five allowed, the result equals `item_legal=True`.

The first defender turn is important even though the anticipated Boss response occurs later. If a Switch is drawn immediately, the defender can use it proactively to change the target being damaged and obstruct the attacker's eventual Prize-taking line. Turn 2 alone has no equivalent benefit in this board. Permitting Item play on turns 3 and 4 jointly already achieves the maximal defensive Switch value, so additional turn-1 permission offers no further benefit once both are open.

For example, allowing Switch **only on defender turn 1** raises the expected attack count from `65/12` to `787/144`, a positive increment of **`7/144`**, even with Item lock on all later relevant turns. Thus a state representation that merely asks whether Switch is playable on the final anticipated gust-response turn can miss a proactive line.

## Validation and an information-set counterexample

[The regression suite](reproduce.py) enumerates all 32 masks, checks their eight exact rational values, asserts irrelevance of turns 2 and 5, and confirms both all-allowed/all-blocked limits against the established [static Item-permission solver](../../tools/two_sided_stochastic_escape.py).

It separately enumerates the **144** physical placements of one Boss and one Switch in the two length-12 decks for every mask, totaling **4,608 full-order physical game trees**. This independent oracle gives both players advance knowledge of their own and their opponent's future deck order, so its information structure deliberately differs from the hidden-draw chance/minimax recurrence.

In **24 masks** the two means agree. In the other **eight masks**, exactly those that allow Switch on turn 3 but prohibit it on turn 4, the full-future oracle produces an expected attack count smaller by **`1/48`**. For the turn-3-only mask, for instance:

- Hidden-order chance/minimax: `11/2 = 5.5` attacker turns.
- Both-players-full-future oracle: `263/48 = 5.4791667` attacker turns.

This is a concrete demonstration that complete physical-deck enumeration with omniscient agents is not automatically a valid validator for decision policies under unknown deck order. Its average may be higher or lower than the correct hidden-order model, depending on which player can exploit future knowledge.

**Additional private-information caveat:** The hidden-order chance/minimax engine still supplies the defender with the attacker's current category-level Boss hand count, which an ordinary Pokémon opponent cannot see. Therefore these findings are exact for the specified perfect-current-count information game. A genuine private-hand Bayesian game needs further research.

The bundled `sv1-194` printing identifies Switch as an Item. The advanced rulebook permits playing Items on your turn unless prevented by an applicable effect, and treats Item-based switching independently from normal Retreat. The mask is a tactical abstraction of such permission. It is not evidence about any specific paper Expanded lock source's timing or legality.

## Reproduction

- [Implementation](../../tools/timed_item_lock_gust.py)
- [32-mask and 4,608-world regression](reproduce.py)
- [CI workflow](../../.github/workflows/validate-timed-item-permission-gust.yml)
- [Static Boss–Switch theorem](../gust_switch_critical_window/)

Run `python results/timed_item_permission_gust/reproduce.py`.

Natural continuation: derive the permission schedule from a source-aware lock engine, resolve when an Active-position lock source enters or leaves play, and test whether a deliberately early Switch can alter the lock source itself. Incorporating the opponent's hidden hand information and finite normal Retreat would improve match realism.
