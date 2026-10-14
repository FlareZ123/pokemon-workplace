# Public identity of a Prize-origin card used before hand entry

This result composes the real Chansey Lucky Bonus and Treasure Energy Prize-origin effect profiles with an ordered batch of unresolved Prize identities.

The model in `tools/physical_before_hand_batch_bridge.py` uses the existing rules-aware E-31 executor, then updates both players' beliefs according to where the card actually went. Cards put into play or attached are public. Cards placed in the taking player's hand remain private to the other player. Cards redirected to the face-up discard pile or Lost Zone become public, and a replacement effect preventing hand entry also prevents hand-bound E-31 activation.

## Exact example

Two initially possible assignments give the opponent P(top=A)=1/2. The actor privately sees Chansey and Treasure Energy when staging both prizes.

When Chansey triggers Lucky Bonus and enters play, the identity revealed publicly updates the opponent to P(top=A)=1. In a counterfactual where Chansey enters private hand, the opponent remains at 1/2 until Treasure Energy is publicly attached. The opponent then updates to 1. If Chansey is redirected to discard, Lucky Bonus cannot activate, and the discard itself publicly reveals the card.

The test checks these probabilities, physical card conservation and the legal replacement gate. It uses real card IDs `sv3pt5-113` and `swsh7-165`.

## Reproduce and limits

Run `python results/pending_prize_before_hand_visibility/reproduce.py`. Automated test: `.github/workflows/validate-pending-prize-before-hand-visibility.yml`.

The model covers direct self-to-Bench or self-attach E-31 effects, including declining the effect. Item-play families, successful recursive additional Prize awards, and general hidden-hand tracking remain outside this bridge. These results concern rules-level information flow and do not establish competitive win rates.

Related: `results/pending_prize_batch_correlation/`, `results/prize_before_hand_destination_gate/`.
