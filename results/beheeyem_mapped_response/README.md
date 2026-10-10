# Town Map Prize selection under opposing N: information survives, but its policy can change

## Research question

The [Town Map face-up Prize upper bound](../beheeyem_mapped_prizes/) showed that choosing a known Beheeyem, Triple Acceleration Energy (TAE), tutor or filler from the original six Prizes can strongly improve next-turn packet access. That analysis preserved the acquired Prize card in hand until the next attack.

If the opponent responds with **N**, the chosen Prize card goes back into the deck with the rest of the player's hand, and the player draws new cards based on remaining Prizes. Does the identity chosen using Town Map still matter? Can the best selection **change** when N is anticipated?

This exact finite study compares three policies for the same known T2 hand and face-up six-Prize composition:

1. **Blind award + opponent N:** randomly take r Prize cards, then N shuffles all hand cards into the deck.
2. **Face-up optimal award + opponent N:** choose r Prize identities to maximize the probability of a second Beheeyem+TAE packet after the N shuffle and redraw.
3. **Face-up award optimized for no opponent reset, followed by surprise N:** choose Prize identities to maximize the uninterrupted-hand packet probability, then experience N anyway. If several choices are equally optimal for the uninterrupted hand, use the one best under N, so measured regret is conservative.

These are action-policy comparisons **conditional on perfect Prize mapping already being active** and r=0,1,2 earned Prizes after the first Mysterious Noise attack. A physical Town Map card, its acquisition and Item-play cost remain excluded.

## Model

The initial conditioned setup is the same three mature-board Basics, six residual T2 hand cards, six physical Prizes, and 45 deck cards. A first Mysterious Noise packet is directly held or rescued by a payable one-copy tutor. Its Beheeyem, TAE and underlying Elgyem are shuffled back, creating the usual **48-card** direct or **47-card** tutor-rescued deck.

For each full T2 hand and face-up six-Prize multiset, the code enumerates every category subset of r distinct physical Prize cards. For each possible selection:

- **No reset payoff:** add those cards to the surviving hand and test the next packet after d random deck draws.
- **Opposing N payoff:** add them to the surviving hand, shuffle that complete hand into the full physical deck, then draw **6-r+d** cards from the newly shuffled deck. Check B+TAE or one missing category supplied by a newly drawn and payable tutor.

All quantities are exact rational expectations over T3 deck randomness. Each hand and Prize state is weighted by its physical multivariate hypergeometric probability.

The model assumes N can be played as a Supporter during the opponent's reply despite the Item lock applied by Mysterious Noise. It also assumes N's standard effect and that first-attack Prize count r is externally fixed, without predicting Knock Outs.

## How much of Town Map's access benefit survives N?

B=4 Beheeyem, T=4 TAE, one Computer Search, d=1 T3 additional blind draw:

| Prize cards awarded | Random Prize, no reply | Mapped Prize, no reply | Random Prize, opposing N | Mapped Prize, opposing N |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1.125764% | **2.926368%** | 2.647861% | **2.923340%** |
| 2 | 1.679597% | **4.452270%** | 1.881457% | **2.095391%** |

At r=1, mapping adds **+1.800604 percentage points** with the hand preserved, but only **+0.275478 percentage points** after N. That retains approximately **15.3%** of the information advantage in this specific packet event.

At r=2, the mapped advantage drops from **+2.772674 percentage points** uninterrupted to **+0.213934 percentage points** after N, retaining approximately **7.7%**.

N neither makes face-up Prize choice meaningless nor preserves its uninterrupted value. Knowing exactly which resource enters a future shuffled draw pool still helps, but much less than immediately placing a missing attack packet card directly into hand.

For four Beheeyem/TAE and one Mysterious Treasure tutor with one awarded Prize and one next-turn draw, mapping after N improves the joint packet event from **2.033551%** to **2.240584%**. The corresponding uninterrupted-hand mapping advantage is much larger: from 0.833836% to 2.229612%.

## Sometimes the optimal Prize card changes if N is expected

The finite study explicitly compares the Prize-card choices optimizing the no-reply and opposing-N futures. For B4/TAE4/Computer Search/d1/r1, **12 of 346** reachable count-level K1 states have **strictly incompatible** optimum choice sets. Their combined probability mass is only **0.007605 percentage points** of all conditioned physical setups, and using the no-reply policy under surprise N loses **0.000077 percentage points** of joint packet success on average. These are rare, but real, policy disagreements.

A strong exact witness explains the mechanism:

- T2 hand: **B1, TAE3, Computer Search1, filler1**.
- T2 first attack uses B1 and TAE1. Remaining hand is **TAE2, Computer Search1, filler1**.
- Original six Prizes: **TAE1, filler5**.
- After attack, T3 deck: **B4, TAE1, no Computer Search, filler43** (48 cards).
- The face-up Prize choice for one earned Prize is **TAE or filler**.

If the opponent leaves the hand alone:

- Choosing **filler** gives the hand two filler cards, enough to pay Computer Search immediately to obtain missing Beheeyem. Packet success is **100%**.
- Choosing **TAE** leaves only one filler, so the tutor normally needs another filler from the one future draw. Packet access is **47/48 = 97.916667%**.
- Thus the **uninterrupted optimum is filler**.

If the opponent will play N:

- The entire hand will be shuffled back into the deck. The extra filler loses its immediate role as the second discard payment, while extra TAE improves the supply of a packet category in the new random draw pool.
- Choosing **filler** yields a next-packet probability of **453176/2869685 = 15.791834%**.
- Choosing **TAE** yields **1096853/5739370 = 19.111035%**.
- Thus the **N-aware optimum is TAE**, with a **3.319201 percentage-point** advantage in this specific state.

This is a concrete example of why discard costs and card-access timing should be evaluated together. A filler card can be the most useful *immediate* Prize pickup because it pays a tutor, while a packet resource can be more useful when a forthcoming hand reset turns the whole selection into future deck density.

## Full finite scan

The exact engine covers 16 B/TAE copy-count pairs, four tutor classes, d=0–5, and r=0–2, yielding **1,152** configurations:

- Face-up optimal Prize selection under N improves next-packet access versus blind selection in **768** parameter configurations.
- At least one strictly conflicting optimal Prize choice between uninterrupted and N-aware plans occurs in **232** parameter configurations.
- No policy conflict is possible for r=0, since no Prize identity is selected.
- In all cases the N-aware policy weakly dominates using a no-reply-optimal Prize choice under N; the nonnegative difference is measured exactly as surprise-N regret.

These results are finite-model computations, not a proof about arbitrary decks or opponent responses.

## Methods and validation

- [Exact N-aware Prize policy](../../tools/beheeyem_mapped_response.py) enumerates every valid r-card Prize subset and computes exact uninterrupted and post-N packet probabilities. It also computes state-weighted policy regret when a no-reply selection is followed by N.
- [Reproduction](reproduce.py) tests all 1,152 scenarios, cross-validates the blind N branch against the independent opposing-Supporter engine, and validates the uninterrupted mapping branch against the earlier Town Map engine, with exact fraction checks and paired target-swap symmetry.
- [Monte Carlo](monte_carlo.py) draws real initial physical hands and Prizes, samples random Prize versus exact-optimal Prize identities for both response hypotheses, shuffles the entire hand back into deck under N, then measures conditional next-packet success in four 200,000-trial scenarios.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-mapped-response.yml) runs both validations.

## Strategic limits and next work

Town Map's presence, acquisition and play timing are external assumptions. The first-attack Knock Out and the opponent's N reply are exogenous events. Every neutral filler can be discarded, and a mature attacker board and T3 draws are assumed feasible. Opponent choice, later Prize race, attacks and other resource uses are not simulated.

These results give a strong reason to integrate **opponent belief and hand-disruption probability** into information-value calculations: the best Prize to take for immediate access can differ from the best Prize to take for subsequent deck density. A useful next stage is to add one physical Town Map copy to the 57-card population and make its ability contingent on actually drawing and playing that Item before the initial Prize award.
