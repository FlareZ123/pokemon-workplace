# Physical revealed-search signaling bridge

## Question

Can a publicly revealed search target selected after K1 be executed as an exact physical card movement while keeping the searcher's private Prize knowledge, the opponent's signaling posterior, the shuffled top, and card conservation synchronized?

Yes.

Implementation: `tools/deck_search_target_signal_physical.py`

Regression: `results/deck_search_target_signal_physical/reproduce.py`

## Transition boundary

The bridge begins from `SearchableDeckPhysicalState`, where the deck is unordered and any previous materialized top relation has already been collapsed.

It derives from exact physical truth:

- the actor's grouped Prize composition;
- current grouped deck-plus-Prize pool counts;
- current deck-plus-Prize pool size.

It then uses the supplied target-selection policy to update observer beliefs after the public target reveal.

The exact searched card copy is materialized from deck and moved to hand. The resulting physical pool is checked against the count change assumed by the belief transition.

Finally, one exact shuffled top copy is materialized and every observer posterior must retain positive support on the exact top/Prize world.

## Exact six-card world

The physical pool contains:

- A in Prize;
- one filler in Prize;
- X in deck;
- Y in deck;
- two fillers in deck.

The observer prior is the same symmetric six-card prior used by `deck_search_target_signal`.

The actor fully inspects the deck, learns grouped Prize composition A=1, X=0, Y=0, and publicly reveals target X under the same deterministic target-selection policy.

The bridge then:

1. materializes the exact X copy from deck;
2. moves that same instance to hand;
3. verifies that the deck-plus-Prize pool lost exactly one X and one total card;
4. materializes Y as one exact post-shuffle top branch.

The resulting material truth is:

- top=Y;
- Prizes=(A, filler);
- searched X in hand.

## Observer divergence

For that exact world:

- the actor assigns P(top=Y)=1/3;
- the opponent assigns P(top=Y)=1/7 after conditioning on the target-X signal.

Both posteriors assign positive probability to the same exact physical world.

The difference is epistemic. The cards themselves are shared physical truth, while each observer conditions on different information.

## Conservation

Per-class totals are identical before the search and after both target movement and top materialization.

The regression also attempts to search the singleton A even though exact physical truth places A in the Prize zone. Materialization rejects that branch because no A copy exists in deck.

This supplies an independent physical legality check alongside the belief-layer target policy.

## Strategic interpretation

The searched card should not be represented only as an abstract target label once a simulator commits to the action.

The public label carries information, while the exact copy moves through physical zones. Those are separate layers that must agree.

This result closes a complete narrow loop:

private full-deck inspection -> public target choice -> opponent Bayesian update -> exact target movement -> shuffle -> exact new top -> truth-support validation.

## Limits

The bridge begins at search resolution. It does not yet execute the Trainer card, pay Quick Ball's discard cost, or consume turn/action permissions.

The exact searched target remains materialized in hand. A future hand-knowledge layer may choose a more explicit representation for publicly known hand cards while allowing hidden exchangeable copies to remain aggregated.

The target-selection policy remains external.

## Next work

The strongest integration is to connect this bridge to the existing atomic Trainer search transaction.

For Quick Ball-like play, that combined action should include:

- Item play permission;
- the exact discard witness;
- the resolving Trainer card;
- typed legal target allocation;
- public target reveal;
- K1 search information;
- opponent target-signal conditioning;
- exact searched-copy movement;
- shuffle and post-shuffle top state.

That would connect current compiler, action-budget, discard-cost, physical-identity, and hidden-information layers in one auditable transaction.
