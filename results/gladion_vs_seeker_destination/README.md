# Gladion destination error under VS Seeker recovery

## Question

`results/literal_gladion_projection/` proves that literal Gladion's self-shuffle into the Prize zone can be projected away for one narrow objective: isolated timed recovery of initially critical Prize cards when no other effect cares where the played Supporter goes.

What happens as soon as the deck contains **VS Seeker**, which can return a Supporter from the discard pile to the hand?

The projection breaks immediately if a simulator interprets the earlier "consumed rescuer" abstraction as "discard the played Gladion." Literal Gladion is not in the discard pile after it resolves, so VS Seeker cannot recycle that played copy.

Implementation: `tools/gladion_vs_seeker_destination.py`  
Reproducer: `results/gladion_vs_seeker_destination/reproduce.py`

## Rules and card-text interaction

The bundled Gladion text takes one face-down Prize card into the hand, then shuffles the played Gladion into the remaining Prize cards. The effect only works when Gladion was played from the hand.

VS Seeker puts a Supporter card from the discard pile into the hand.

The advanced rules establish the normal rule that a used Supporter is discarded, while also establishing that current card text takes priority when it contradicts the basic rules. Gladion's self-shuffle therefore changes its real destination before VS Seeker can treat it as a discard-pile Supporter.

This result compares two exact policies:

- **literal destination:** played Gladion enters the Prize zone;
- **naive discard destination:** played Gladion enters the discard pile and may later be recovered by VS Seeker.

The second branch is an intentionally incorrect counterfactual used to measure the error caused by overextending the consumed-rescuer abstraction.

## Minimal deterministic counterexample

Consider a state with:

- two initially critical Prize cards remaining;
- one Gladion in hand;
- one VS Seeker in hand;
- no other Gladion copies available;
- two remaining Supporter windows.

In the literal game-state model, the maximum probability of recovering both critical cards is **0%**. Gladion rescues one critical card, then the played Gladion is in the Prize zone. VS Seeker has no Gladion in the discard pile to recover.

In the naive discard model, success is **100%**. Turn one incorrectly sends Gladion to the discard pile after rescuing the first critical. Turn two uses VS Seeker to return that same Gladion and rescues the second critical.

This is a state-level proof that the consumed-rescuer projection cannot be reinterpreted as a physical discard transition once discard-pile Supporter recovery enters the model.

## 60-card exact baseline

Use:

- 60 cards;
- 6 Prize cards;
- valid 7-card opening;
- 12 setup-eligible starters;
- 4 modeled non-starter critical singletons;
- 1 Gladion;
- 0 to 4 VS Seeker;
- remaining cards as filler;
- one random draw at the start of each rescue turn;
- condition on at least one critical being initially Prized.

The literal column is independent of VS Seeker count in this isolated model because there is no Supporter in the discard pile for VS Seeker to recover. The incorrect model gains artificial recycling after the first Gladion use.

| VS Seeker | Turn 2 literal | Turn 2 naive discard | Gap | Turn 4 literal | Turn 4 naive discard | Gap |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 12.592135% | 12.592135% | 0.000000 pp | 15.540184% | 15.540184% | 0.000000 pp |
| 1 | 12.592135% | 12.810655% | 0.218519 pp | 15.540184% | 15.890736% | 0.350552 pp |
| 2 | 12.592135% | 13.003857% | 0.411722 pp | 15.540184% | 16.190500% | 0.650316 pp |
| 3 | 12.592135% | 13.174241% | 0.582106 pp | 15.540184% | 16.446023% | 0.905839 pp |
| 4 | 12.592135% | 13.324103% | 0.731968 pp | 15.540184% | 16.663116% | 1.122932 pp |

There is no turn-1 gap because the modeled discard pile begins without Gladion. The false edge only appears after a Gladion has been played once.

The error continues accumulating at longer horizons. With one Gladion and four VS Seeker, the conditional overstatement reaches:

- **1.559869 pp** by turn 6;
- **2.037797 pp** by turn 8;
- **2.546887 pp** by turn 10.

These are still narrow baseline numbers rather than deck-level performance estimates. The deterministic microstate above shows that individual states can have a much larger error than the aggregate average.

## Why the earlier projection remains valid in its original domain

`results/literal_gladion_projection/` projected away the count of Gladion in the Prize zone because no modeled action could use that count to improve the isolated objective. That proof remains correct.

VS Seeker adds a new zone-sensitive action. Once the model distinguishes "discard pile" from "Prize zone," the destination of the played Supporter becomes decision-relevant. The correct extension is therefore to restore the physical destination in canonical state rather than reinterpret the old projection as a discard.

This distinction is methodological:

- an **evaluation projection** may erase state that is irrelevant to a stated objective and action set;
- an **execution transition** must still send the physical card to the zone specified by its text.

The two layers should not be conflated.

## Validation

The reproducer asserts:

1. the deterministic two-critical / one-Gladion / one-VS-Seeker counterexample is `0%` literal versus `100%` naive-discard success;
2. with zero VS Seeker, both destination models are exactly identical;
3. the literal branch is invariant when VS Seeker copies merely replace filler in this isolated setup;
4. the naive-discard branch gains only from its deliberately false recovery edge;
5. setup-conditioned state mass sums to one for the 60-card calculations.

The calculations are exact dynamic programs; no Monte Carlo sampling is used.

## Limitations

The model begins with no Gladion in the discard pile. Real decks can legitimately put Gladion there through another effect, such as Battle Compressor, after which VS Seeker may legally recover it. This result isolates only the **post-play destination** of a Gladion that resolves normally.

It also excludes Item lock, other Supporters, other VS Seeker targets, Battle Compressor, ordinary Prize-taking, Prize manipulation, opponent interaction, and competing uses of VS Seeker. VS Seeker is treated as having no opportunity cost beyond consuming itself.

## Strategic and simulator implication

A simulator may safely use the consumed-rescuer projection for the narrow probability calculation validated in `literal_gladion_projection`. It must not materialize that projection as `Gladion -> discard` in a richer state engine.

The canonical transition should preserve:

`hand Gladion -> Prize zone`

after Gladion resolves. Discard-based connectors such as VS Seeker should query the actual discard zone and therefore find no played Gladion there.

This is a concrete example of why state abstraction and physical card movement need separate interfaces.

## Next useful work

A strong next composition is the legitimate `Battle Compressor -> Gladion in discard -> VS Seeker -> Gladion in hand` route alongside the illegal post-play recycle route. One shared model could then distinguish how a Gladion entered the discard pile, preserve VS Seeker's valid current-window access, and prevent already-played Gladion from being recovered unless another effect later moves it out of the Prize zone.
