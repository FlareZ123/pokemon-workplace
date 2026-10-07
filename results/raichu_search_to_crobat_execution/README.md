# Harto Miki Raichu/Electrode: physical search-to-Crobat execution

## Question

The Raichu access models assign Quick Ball and Ultra Ball different Dark Asset draw widths after they search Crobat V.

Can those representative lines be replayed through the repository's canonical physical Trainer transaction and typed Bench state, rather than relying only on hand-size arithmetic?

Yes.

Implementation: `tools/raichu_search_to_crobat_execution.py`  
Regression: `results/raichu_search_to_crobat_execution/reproduce.py`

## Card-text witness

The bundled Sword & Shield records used by the bridge are:

- Quick Ball `swsh1-179`: discard another card, search the deck for a Basic Pokémon, reveal it, put it into hand, then shuffle;
- Ultra Ball `swsh9-150`: discard two other cards, search the deck for a Pokémon, reveal it, put it into hand, then shuffle.

Crobat V is a Basic Pokémon, so it satisfies either selector.

The bridge represents these two audited effects as narrow `CompiledTrainerSearchProfile` objects and sends them through the existing `execute_trainer_search_transaction()` path. It therefore inherits exact discard witnesses, Item-play locks, typed target allocation, the temporary resolving-Trainer zone, deck-to-hand target movement, final Trainer disposal, and per-class conservation checks.

## Seven-card action snapshot

Both witnesses begin with seven cards in hand after setup and the ordinary draw, matching the probability models.

### Quick Ball

Physical sequence:

`7 -> play Quick Ball -> 6 -> discard 1 -> 5 -> search Crobat V -> 6 -> Bench Crobat V -> 5`

The canonical transaction and Bench bridge produce:

- hand after search: **6**;
- hand after Crobat V is Benched: **5**;
- Dark Asset draw-to-six width: **1**.

### Ultra Ball

Physical sequence:

`7 -> play Ultra Ball -> 6 -> discard 2 -> 4 -> search Crobat V -> 5 -> Bench Crobat V -> 4`

The executed state produces:

- hand after search: **5**;
- hand after Crobat V is Benched: **4**;
- Dark Asset draw-to-six width: **2**.

This independently confirms the cost-to-draw coupling used by `raichu_dark_asset_search` and `raichu_dark_asset_followup`.

## Bench capacity counterexample

A second Quick Ball witness begins from a full five-slot Bench.

The Quick Ball transaction itself remains executable:

- the Item and one exact discard card move to discard;
- Crobat V moves from deck to hand;
- card totals remain conserved.

The next hand-to-Bench transition fails because there is no Bench slot.

The result therefore ends with Crobat V in hand and **zero Dark Asset draw**.

This is a concrete separation between search success and line success. Search connectivity reaches Crobat V, while the intended draw-engine continuation still requires a physical Bench slot at the moment of entry.

## Other mechanical gates

The regression also verifies:

- Item lock rejects Quick Ball before the search transaction resolves;
- Ultra Ball is rejected when the supplied discard policy exposes only one disposable card;
- protected hand cards marked unavailable to the discard selector stay in hand;
- all represented card-class totals are conserved across both successful lines.

## Architectural implication

The deck-specific probability model and the shared physical kernels now agree on the representative search-to-Crobat transitions.

The probability layer asks how often a state with the required card identities and discard capacity occurs.

The execution layer verifies what happens once that state is selected:

`exact payment -> Trainer resolution -> target movement -> Bench entry -> trigger -> draw width`

This keeps Dark Asset's draw count tied to physical hand mutation and makes Bench saturation an explicit failure mode instead of an informal caveat.

## Limits

The bridge stops immediately before drawing Dark Asset cards. It computes the draw-to-six width from the physical hand count but leaves exact deck draws to the probability model.

It does not yet execute:

- Dark Asset's once-per-turn restriction;
- Ability lock;
- opponent-controlled Bench contraction;
- another searched Crobat V in the same turn;
- Forest Seal Stone attachment or VSTAR-Power consumption;
- exact K0/K1 belief updates caused by the search;
- shuffled deck order.

The narrow Quick Ball and Ultra Ball profiles are card-text-audited local adapters. They are not a general single-output Trainer parser.

## Next useful work

The strongest integration is to execute the bounded post-Dark-Asset connector continuation from `raichu_dark_asset_followup` on physical state.

A representative Quick Ball witness can:

1. pay the first discard and search Crobat V;
2. Bench Crobat V and draw one exact connector;
3. verify that two residual disposable cards are still present;
4. execute the newly drawn Ultra Ball or Computer Search through the canonical transaction;
5. compare the resulting material state with the probability model's success predicate.

That would validate the new residual-payment gate end to end.
