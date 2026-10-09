# Physical bottom-of-deck redraw execution

## Scope
Six literal paper-Expanded hand-return effect families are resolved as physical two-player ordered deck/hand state transitions. The source print witnesses are Iono (sv2-185), Marnie (swsh1-169), Lucian (sv6-157), Thievul Fumbling Hands (swsh7-105), Kingdra Seething Currents (swsh11-37), and Skwovet Nest Stash (sv1-151).

The kernel in `tools/bottom_hand_redraw_execution.py` applies after the caller has legally selected the card/Ability and any optional effect. It accepts explicit randomized permutations of bottomed hands, draws from the preexisting top of each deck, and can cross into bottomed cards when the original deck is shorter than the draw.

## Distinct mechanics
Iono, Marnie, Lucian and Thievul bottom both hands, then draw for both players if **either player** moved at least one card. Iono draws the respective remaining Prize count; Marnie draws five for the acting player and four for the opponent; Lucian independently flips coins for draws of six on heads or three on tails; Thievul draws four each.

Kingdra bottoms only a chosen player's hand and draws four for that player when the returned hand was nonempty. Skwovet bottoms the acting player's hand and draws one when nonempty.

**Cross-player coupling witness:** if the acting player starts with an empty hand and two cards [A,B] in deck, while the opponent has [D] in hand and [C] in deck, Iono causes the acting player to draw A and B when they have two Prizes remaining, even though the acting player returned nothing. The opponent draws C and D, capped to physical cards in the deck.

**Short-deck boundary witness:** a player with old deck [A,B] and hand [X,Y,Z] can bottom the hand in randomized order [Z,X,Y] with Marnie and immediately draw [A,B,Z,X,Y]. Bottomed cards can reappear in the same effect when the requested draw reaches past the preexisting deck.

## Reproducibility
`results/bottom_hand_redraw_execution/reproduce.py` enumerates two-player short deck/hand states, permutations of returned hands, the four both-player effects, Lucian coin patterns, two Kingdra target choices and Skwovet. All cases validate physical conservation and named effect draw counts. Separate assertions guard the coupled empty-hand condition, short-deck boundary and invalid randomized-order inputs.

This is an effect resolver with externally supplied legality and stochastic outcomes, not a full turn engine. Ability suppression, evolution status, Supporter restrictions, hand-move triggers and matchup-dependent strategy remain for later work.
