# Retreat payments change stochastic gust value under Item lock

## Research question

When the opponent can normally Retreat, does the number of physical attached Energy cards matter even if the total Energy *provided* is identical? How does this interact with Boss's Orders still hidden in the attacker's draw pile, with the defender's Switch Item and Item-play permission, and with whether a simulator incorrectly grants knowledge of future draws?

This research extends [two-sided stochastic Boss/Switch acquisition](../two_sided_stochastic_escape/) by composing it with the previously validated [physical Retreat and adversarial promotion kernel](../typed_retreat_gust/). It uses the existing `tools.typed_retreat_gust.Target` and `retreat_payment_remainders`; its new exact chance/minimax engine is [`tools/two_sided_typed_retreat_draw.py`](../../tools/two_sided_typed_retreat_draw.py).

## State and rules

The opponent's board records each Pokémon's Prize reward, hits remaining, Retreat Cost, physical attached Energy-card unit tuple, and any Retreat prohibition. A normal Retreat is allowed once per intervening defender turn if the Active's attached Energy can satisfy the cost, with a whole-card Energy payment. The defender chooses among physically distinct inclusion-minimal discard remainders, preserving the outgoing Pokémon and its damage on the Bench. It may alternatively play an available Switch Item if Item play is permitted. Boss's Orders may gust any opponent Bench target at most once per attacking turn.

A prior [restricted-objective minimal-payment result](../typed_retreat_payment_pruning/) supports considering inclusion-minimal payments here, because the model includes no effects rewarding Energy discards, returns to hand, or lower remaining attached Energy. This abstraction is invalid in broader mechanics with effects such as Dashing Pouch or Melt Away.

The bundled card data verifies Double Colorless Energy `bw11-113` provides two Colorless Energy, and Switch `sv1-194` is the relevant switching Item. The advanced rulebook distinguishes normally Retreating by discarding Energy from using an Item to Switch, and permits discarding one multi-unit Energy card to satisfy smaller requirements.

Both players draw only their one normal card per turn from separate finite piles and optimize expected number of attacks for an attacker to win six Prizes. **Information-set caveat:** The defender's adversarial policy is given the attacker's current Boss count in hand, as well as category-level deck counts. Such opponent-hand information is concealed in ordinary play. Results therefore characterize a full-current-count information game and do not establish optimal outcomes for private opponent hands. Opponent attacks, normal Energy attachments, Trainer search, Prize draws, Pokémon death timing beyond one-hit KO, alternate effects, evolving, ability locks and switching trigger effects are excluded. Static Item lock affects Switch but does not prevent ordinary payable Retreat.

## Constructed physical-Energy counterexample

The defender has three identical three-Prize Pokémon, each requiring **three hits** and each with Retreat Cost one. The attacker needs six Prizes, starts without Boss in hand, and has two Boss copies in a 12-card draw pile with ten inert cards. Item play is disabled; the defender has twelve inert draws and no other actions.

Compare two setups with exactly two Energy units attached to *each* defending Pokémon:

1. One Double Colorless Energy card per Pokémon, represented by `(2,)`. A cost-one Retreat discards the entire DCE.
2. Two separate Basic Energy cards per Pokémon, represented by `(1,1)`. Each cost-one Retreat can discard one Basic and leave the second for another turn.

| Attached energy on each defending Pokémon | No Boss | Two unseen Boss | Two Boss + one hidden Switch when Items permitted |
| --- | ---: | ---: | ---: |
| One DCE (two units on one physical card) | 8 | **493/66 = 7.469697** | 749/99 = 7.565657 |
| Two Basic cards (one unit apiece) | 8 | **169/22 = 7.681818** | 169/22 = 7.681818 |

The two-Basic setup requires **7/33 additional expected attacker attacks** despite having the same Energy units and Retreat Cost as the DCE setup. Without Boss, both configurations require eight attacks, so the difference is *contingent on future gust access*. One hidden Switch (12-card defender deck) increases the defender's attack delay in the DCE case when Items are permitted, but has no additional value in this two-Basic fixture. With Item lock, Switch cannot be used, but payable Retreat survives.

This is a conditional endgame, not a general assertion that Basic Energy is stronger or that an Item lock should be adopted in a particular deck.

## Validation against independent existing models

[`reproduce.py`](reproduce.py) exhaustively checks **11,232** deterministic-limit configurations against the existing `tools/typed_retreat_gust.py` minimax solver. Bosses and Switches are put in initial hands, making stochastic draws inert. Boards contain two or three Pokémon with 1/3 Prize reward, 1..3 hits, Retreat Cost 1/2 and four Energy-card patterns; source permission and Trainer budgets vary. All exact comparisons pass.

The zero-payable-Retreat special case agrees in another **18** configurations with the source-free two-sided stochastic Boss/Switch model. Assertions also verify card text and the two exact whole-card Retreat payment remainders.

## A caution about clairvoyant physical draw-order oracles

The earlier two studies happened to obtain equality between a hidden-order chance/minimax DP and an oracle that fixes all deck positions in advance, then lets **both players know the entire future order**. That equality is not universal.

For the present DCE endgame with two Boss in twelve cards, enumerating all `C(12,2)=66` complete known draw orders gives an average of **83/11 = 7.545455** attacks: 45 worlds take eight, 12 take seven, and nine take six. The correct **nonclairvoyant** chance/minimax expectation is **493/66 = 7.469697**, differing by exactly **5/66**. The oracle grants future-draw knowledge to *both adversarial players*, which can improve the defender's policy enough to hurt the attacker.

For the two-Basic fixture, the corresponding means happen to agree at `169/22`. A physical-order oracle is therefore a check for concrete special fixtures only when its information assumptions have been separately justified. It is not a general independent validator of hidden-order planning.

## Reproduction and future work

Run `python results/stochastic_retreat_payment_bridge/reproduce.py` from the repo root. See [source](../../tools/two_sided_typed_retreat_draw.py), [regression script](reproduce.py), and [CI](../../.github/workflows/validate-stochastic-retreat-payment-bridge.yml).

Next: model dynamic Item locks, attack-induced temporary Retreat prohibition, opponent's own Energy attachments, and cards changing costs or returning paid Energy. In wider games, the safe payment-pruning rule needs explicit preconditions and a richer action set.
