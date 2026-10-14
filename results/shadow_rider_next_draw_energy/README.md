# Shadow Rider: next natural draw after the Radiant two-VMAX launch

## Strategic question

The Aichi champion Shadow Rider list can use Mysterious Treasure to discard a card, find Radiant Eternatus, and immediately put two Shadow Rider VMAX from the deck onto its Bench. The previous exact study (shadow_rider_energy_reserve) calculated how frequently a Basic Psychic Energy remains in hand directly after that opening action.

The next turn begins with a natural draw. That draw can restore a missing Psychic Energy and permit an Underworld Door attachment even when the first Treasure payment spent the only Psychic that was initially held. How much does one actual next-turn draw recover under the source-deck physical Prize and search constraints?

## Exact source-deck transition

This study uses the same published Aichi champion 60-card source, seven-card Basic-valid opening, six hidden Prizes, one first-turn draw going second, and two-VMAX Treasure-only route.

After the first natural draw the deck has 46 cards. A successful Mysterious Treasure retrieves Radiant Eternatus and shuffles; Climactic Gate retrieves two Shadow Rider VMAX and ends the player's turn. Thus the next natural draw comes from a shuffled **43-card deck**, absent opponent-induced deck changes.

The 37 broad "other" copies in the opening model include 11 Basic Psychic Energy. For each exact physical opening / six-Prize / first-draw state, record:

- h: remaining broad-other cards visible in the player's hand;
- p: broad-other cards hidden among the Prizes;
- d = 37 - h - p: broad-other cards still in the deck;
- t: Mysterious Treasure copies held.

For 11 Psychic Energy placed uniformly among those 37 physical positions, the exact joint distribution of hand Psychic X, Prized Psychic Y, and deck Psychic Z is

P(X=x,Y=y,Z=z | h,p,d) = C(h,x) C(p,y) C(d,z) / C(37,11), with x+y+z=11.

After paying one Psychic Energy (or optionally a spare second Treasure), the model checks whether enough Psychic Energy is already held or the next natural draw hits one of Z Psychic cards among the 43 remaining. It never assumes a successful draw where the Energy was Prized.

## Exact next-turn resource access

Probabilities below are among Basic-valid source-deck openers, conditioned on six physical Prizes and the first going-second natural draw. All rows additionally require the initial Treasure -> Radiant -> two-VMAX launch.

| Psychic Energy copies in hand after one later natural draw | Energy pays Treasure | Energy or spare Treasure pays |
| ---: | ---: | ---: |
| At least 0 (search cost payable) | 24.843972% | 26.390182% |
| **At least 1** | **14.728450%** | **16.990258%** |
| At least 2 | 4.958161% | 6.538724% |
| At least 3 | 0.954758% | 1.472860% |

Relative to the previous immediately-after-payment endpoint, one natural draw increases the at-least-one-Psychic access probability from 12.119811% to **14.728450%** under Energy payment, or from 14.526379% to **16.990258%** when a spare Treasure is an allowed cost.

The next natural draw recovers some of the initial Energy payment's cost. The gap remains substantial because no relevant Psychic Energy can be drawn when all remaining copies are in the Prize cards, discard pile or hand, and because only one card is drawn.

## Interpretation

A held Psychic Energy after the next natural draw is a necessary resource to announce an Underworld Door activation and attach to a Benched Psychic Pokémon on that turn. The modeled successful launch has already placed two Psychic VMAX on Bench, but this study does not model their later Knock Outs, opponent Item/Ability locks, hand disruption, additional Trainer draws, or other choices.

This is an exact conditional *resource-access* model, not a simulated turn-two attack, match outcome, or recommendation to remove cards. The Energy-versus-spare-Treasure payment comparison is a declared discard preference, not a universally optimal policy.

## Independent verification

tools/shadow_rider_next_draw_energy.py enumerates the grouped 60-card source physical opening/Prize/first-draw states. Its 154 distinct (visible filler, Prized filler, held Treasure) probability buckets collapse exactly to the existing 22-bucket Mysterious Treasure payment model.

An independently written physical-card oracle exhaustively enumerates a source-shaped 11-card toy with two Psychic filler cards, labels all cards, checks actual sequential searches, and draws a specific next card from the post-search two-card deck. Its **36,624 weighted chronological toy worlds** match every exact prediction at thresholds 0, 1, 2, with and without spare Treasure payment.

The source print IDs, Climactic Gate's turn-ending text, and Underworld Door's hand-Psychic condition are checked by the reproducer.

Run results/shadow_rider_next_draw_energy/reproduce.py or manually dispatch .github/workflows/validate-shadow-rider-next-draw-energy.yml.
