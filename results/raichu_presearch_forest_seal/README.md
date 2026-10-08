# Harto Raichu: Forest Seal Stone can establish K1 before Quick Ball

## Question

The Harto Raichu K0 result found a 3.921476 percentage-point gap between the best observation-consistent Quick Ball payment policy and a hidden-state oracle.

Can any part of that gap be converted into a legal line by establishing exact Prize knowledge before paying Quick Ball?

Yes, in a small but concrete visible subbranch.

Implementation: `tools/raichu_presearch_forest_seal.py`  
Reproducer: `results/raichu_presearch_forest_seal/reproduce.py`

## Rules and card-text basis

Forest Seal Stone grants its attached Pokémon V the Star Alchemy VSTAR Power, which searches the deck for any one card.

The baseline Harto branch already requires at least one visible Gladion. Gladion can look at the face-down Prize cards and put one of them into hand.

The Advanced Player's Rulebook states that announced Abilities can ordinarily be used from either the Active Spot or Bench unless specified otherwise, and deck search exposes the deck contents to the searching player. The repository's K0/K1 convention treats that first full deck inspection as the point where a sufficiently skilled player can infer exact Prize composition.

Therefore, when Forest Seal Stone and a visible Crobat V host are available before Quick Ball's discard:

- if Alolan Raichu is in the deck, Star Alchemy searches it directly;
- if Alolan Raichu is Prized, Star Alchemy reveals that fact through full-deck inspection, then the already-visible Gladion can take the Raichu from the Prize cards.

This decision uses only information visible before the search. It does not choose between hidden worlds.

## Observable host condition

The extension conservatively recognizes a visible Forest Seal line when:

- Forest Seal Stone is in the action hand; and
- either the setup Active is Crobat V, or another Crobat V is in the action hand and can be benched as the host.

No unobserved Crobat V is credited.

The underlying branch is unchanged:

- Alolan Raichu is not visible in the opening plus first draw;
- Quick Ball is visible;
- at least one Gladion is visible;
- at least one conservative disposable is visible.

## Exact result

Across the same 1,331 visible observations as the baseline model:

| Quantity | Exact modeled value |
| --- | ---: |
| Forest-Seal-hosted observations | 244 / 1,331 |
| Probability mass of hosted Forest Seal line within branch | **1.822834114%** |
| Baseline K0 success inside that hosted subbranch | **85.487944013%** |
| Forest Seal first success inside hosted subbranch | **100%** |
| Baseline optimal K0 branch success | **32.988188975%** |
| With hosted Forest Seal first | **33.252719682%** |
| Gain | **+0.264530707 percentage points** |
| Hidden-state oracle | **36.909665108%** |
| Remaining oracle gap | **3.656945426 percentage points** |
| Original oracle gap recovered | **6.745692139%** |

The extension recomputes the complete grouped opening, draw, and Prize state space. As a regression, its branch mass, baseline optimal K0 mass, and hidden-state oracle mass must exactly match the existing `raichu_k0_discard_policy` result before the new line is credited.

## Strategic interpretation

The earlier 3.921476-point oracle gap is not entirely unreachable hidden-information value.

A visible search action can sometimes move the player from K0 to K1 before the discard deadline. In this specific subbranch, the information action is stronger than pure inspection because Star Alchemy directly solves the deck-resident target world and reveals the Prize-resident world early enough for Gladion to solve it.

This creates a useful sequencing distinction:

1. Oracle value is an upper bound obtained by granting hidden information for free.
2. Information-action value comes from legal actions that reveal the hidden state before the decision.
3. Direct search value may be entangled with the information value because the same action can also satisfy the endpoint.

An optimizer should search for legal information-acquisition actions before treating a K0/K1 gap as irreducible.

## Connector domination implication

On the modeled same-turn Raichu-access endpoint, once a hosted Forest Seal Stone is visible, the Quick Ball payment decision is dominated by using Star Alchemy first.

That does not make Quick Ball globally dominated. Quick Ball may still matter for later board development, Crobat Dark Asset, or other objectives after Raichu has been secured.

The result is endpoint-specific.

## Limits

This remains the same narrow same-turn Alolan Raichu access objective as the baseline model.

It assumes:

- the once-per-game VSTAR Power is unused;
- the chosen Crobat V host can legally receive Forest Seal Stone;
- a Bench slot is available when the host is in hand;
- the Supporter window is available when Gladion is needed;
- consuming the VSTAR Power has no modeled future opportunity cost.

Those assumptions are deliberately visible rather than folded into the headline probability.

A full match policy could rationally decline Star Alchemy even when it guarantees the local endpoint because Forest Seal Stone has discrete future value elsewhere.

## Next useful work

The remaining 3.656945-point oracle gap should be partitioned by other legal pre-Quick-Ball information or direct-access actions.

Visible Ultra Ball and Computer Search are especially interesting because they can themselves inspect the deck, but their two-card payments create a new sequencing and discardability problem rather than a free information action.

A useful follow-up is to compare:

- Quick Ball first under the exact K0 payment rule;
- Ultra Ball or Computer Search first when payable;
- hosted Forest Seal first;
- mixed policies chosen only from the visible observation.

That would measure how much of the current oracle gap is a true information limit and how much is an artifact of fixing Quick Ball as the first connector.
