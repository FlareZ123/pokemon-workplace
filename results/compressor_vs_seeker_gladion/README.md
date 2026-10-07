# Battle Compressor + VS Seeker as provenance-aware Gladion access

## Question

Can an exact timed Prize-rescue model represent the legitimate Expanded route

`Battle Compressor -> Gladion in discard -> VS Seeker -> Gladion in hand -> play Gladion`

while still preventing the illegal post-play recycle identified in `results/gladion_vs_seeker_destination/`?

Yes. The required distinction is **zone provenance**: a Gladion placed into the discard pile by Battle Compressor is a legal VS Seeker target, while a Gladion that resolves normally moves into the Prize zone and is no longer in the discard pile.

Implementation: `tools/compressor_vs_seeker_gladion.py`  
Reproducer and labeled validation: `results/compressor_vs_seeker_gladion/reproduce.py`

## Model

The exact dynamic program uses the same accepted-opening and initial-Prize structure as the other rescue baselines. Each modeled turn begins with one random draw, then allows Item actions before at most one Gladion play.

The state tracks Gladion separately in hand, discard pile, Prize zone, and deck. It also tracks Battle Compressor and VS Seeker separately in hand and deck.

### Battle Compressor transition

A used Battle Compressor can move up to three modeled Gladion copies from deck to discard. The deck count shrinks accordingly. The optimizer may hold the Compressor because moving Gladion out of the deck early can remove a future natural draw if VS Seeker is not yet available.

### VS Seeker transition

A used VS Seeker moves one discarded Gladion into the hand. Multiple Items may be used in the same turn, so Battle Compressor followed immediately by VS Seeker creates a valid current-window route.

### Gladion transition

After a Gladion rescues one initially critical Prize, the played Gladion moves from hand into the Prize zone. It does **not** enter the discard pile.

The implementation also has an intentionally incorrect `played_to_discard=True` counterfactual so the post-play destination error can be measured inside the same access network.

## Complementarity result

Use a 60-card baseline with 12 setup-eligible starters, 4 modeled non-starter critical singletons, 1 Gladion, varying Battle Compressor / VS Seeker counts, 6 Prize cards, a valid 7-card opening, one random draw per rescue turn, and condition on at least one critical being initially Prized.

Literal conditional rescue success is:

| Battle Compressor | VS Seeker | Turn 1 | Turn 2 | Turn 3 | Turn 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 11.118111% | 12.592135% | 14.066160% | 15.540184% |
| 1 | 0 | 11.118111% | 12.592135% | 14.066160% | 15.540184% |
| 0 | 1 | 11.118111% | 12.592135% | 14.066160% | 15.540184% |
| 1 | 1 | 12.129941% | 13.886792% | 15.669521% | 17.475441% |
| 2 | 2 | 14.778970% | 17.186688% | 19.646805% | 22.145546% |
| 4 | 4 | 23.083729% | 27.058981% | 30.998331% | 34.856791% |

One half of the two-Item route is insufficient in this narrow model. Battle Compressor without VS Seeker strands Gladion in discard. VS Seeker without a prior discard source has no Gladion target. Together they create targeted same-window access.

This is a concrete example of **path complementarity**: card counts cannot be valued independently when an access route requires the conjunction of two different physical transitions.

## Provenance prevents post-play recycling

The same model can deliberately send played Gladion to discard to reproduce the destination error.

For the 4 Battle Compressor / 4 VS Seeker package:

| Horizon | Literal destination | Naive played-to-discard | Overstatement |
| ---: | ---: | ---: | ---: |
| Turn 1 | 23.083729% | 23.083729% | 0.000000 pp |
| Turn 2 | 27.058981% | 28.179794% | 1.120814 pp |
| Turn 3 | 30.998331% | 32.458236% | 1.459905 pp |
| Turn 4 | 34.856791% | 36.683222% | 1.826431 pp |

The turn-1 values agree because no already-played Gladion exists yet. From turn 2 onward, the incorrect state gains artificial VS Seeker targets.

This demonstrates why a discard zone should carry physical provenance through execution. “Gladion is accessible through VS Seeker” is true only when a Gladion actually entered discard by a legal transition such as Battle Compressor or another discard effect.

## Independent validation

The reproducer contains a labeled 10-card model with 3 starters, 2 critical cards, 1 Gladion, 1 Battle Compressor, 1 VS Seeker, 2 filler cards, a 3-card opening, 2 Prize cards, and 2 rescue turns.

It enumerates every accepted opening hand and disjoint Prize set, then averages over labeled future draws. Item actions physically move the exact labeled Gladion between deck, discard, hand, and Prize zone.

The labeled calculation gives:

- `P(any critical initially Prized | valid start) = 40.448179%`;
- conditional rescue success = `57.590028%`.

Those values match the category dynamic program to floating-point precision.

The reproducer also checks that Battle Compressor alone leaves literal rescue unchanged, VS Seeker alone leaves literal rescue unchanged when the discard starts without Gladion, the 1/1 pair strictly improves current-window access, the incorrect post-play discard branch is never below the literal branch in the tested baseline because its only difference is an extra recovery edge, and total setup-conditioned state mass is one.

## Relation to connector domination

The model deliberately treats Battle Compressor and VS Seeker as dedicated Gladion-access resources. Real Expanded decks rarely do.

Battle Compressor can have high-value discard payloads, and VS Seeker can recover many different Supporters. Spending both on Gladion may be dominated by another line even when the route is mechanically available.

This result therefore answers a narrower question: **when the two cards are allocated to Gladion access, what exact timing and zone transitions make the route executable?** A broader optimizer should place target choice and connector contention on top of this physical transition kernel.

## Simulator implication

A robust access engine should distinguish at least:

`deck Gladion --Battle Compressor--> discard Gladion`

`discard Gladion --VS Seeker--> hand Gladion`

`hand Gladion --play/resolve--> Prize-zone Gladion`

The final edge closes the VS Seeker route for that copy. Reusing a generic state label such as “spent Supporter” without its physical destination is insufficient once discard-pile recovery is modeled.

## Limitations

The model excludes Item lock, Supporter lock, other VS Seeker targets, other Battle Compressor payloads, ordinary Prize-taking, other discard effects, Prize manipulation, hand costs, opponent interaction, and matchup-dependent criticality.

Battle Compressor may discard up to three modeled Gladion copies, but the model does not give value to its other two potential discard targets. Likewise, VS Seeker has no target choice beyond Gladion.

## Next useful work

The next strong extension is **connector target contention** inside this provenance-aware state: give Battle Compressor at least one alternative valuable payload and VS Seeker at least one competing Supporter target with its own deadline. That would connect the exact physical route here to the repository's connector-domination and competing-deadline results.
