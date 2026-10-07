# Atomic Computer Search: cost, private target, K1, shuffle, and conservation

## Question

Can the bundled Computer Search interaction be executed as one auditable transaction that preserves its Item play gate, exact discard cost, mandatory private target movement, Prize-information update, hidden target identity, shuffle, and physical conservation?

Yes.

Implementation: tools/computer_search_private_transaction.py
Regression: results/computer_search_private_transaction/reproduce.py

## Card witness

The bundled bw7-137 Computer Search record is an Item and ACE SPEC. Its effect discards two cards from hand, searches the deck for one unrestricted card, puts that card into hand, and shuffles.

The Advanced Player's Rulebook's unrestricted-search exception makes that one-card selection mandatory once the search occurs and the deck is nonempty.

The searched card is not revealed by the bundled effect text, so target identity is private information.

## Composition boundary

This result leaves the existing typed Trainer-search transaction unchanged. That engine is built around selector-limited search, where physical target consumption can match useful typed output.

Computer Search instead uses a dedicated adapter that composes existing primitives:

1. require the Item-play channel;
2. move the physical Computer Search copy from hand to the resolving-Trainer zone;
3. apply an exact two-card discard witness;
4. derive K1 and observer-private target beliefs from the post-cost physical state;
5. materialize the exact private target into hand;
6. materialize one exact post-shuffle top;
7. move Computer Search from resolving to discard;
8. verify per-card-class conservation.

The Supporter budget is preserved because Computer Search is an Item.

## Exact regression

The exact hidden pool contains A, X, Y, and three fillers. Prizes are A plus filler. The searchable deck is X, Y, and two fillers.

The hand contains Computer Search, discard card D1, and discard card D2.

The transaction pays D1 and D2, privately selects X under the uniform target policy, and materializes Y as the shuffled top.

Final physical state includes Computer Search, D1, and D2 in discard; private X as a materialized hand instance; exact Y as deck_top; and unchanged Prize instances A and filler.

Per-class totals are identical before and after.

## Observer result

The actor knows the exact Prize composition and that X was privately selected. The actor therefore assigns P(top=Y)=1/3.

The observer sees the Computer Search action and shuffle while target identity remains private. Under uniform private selection, the observer assigns P(top=Y)=1/6.

Both beliefs support the same exact physical world.

## Mechanical gates

The regression additionally verifies one-card discard payment is rejected, Item lock rejects the entire transaction before costs or search resolve, and an already-spent Supporter use remains unchanged.

## Architectural implication

A generic search-to-target edge is too small for Computer Search. One physical play spans action permission, exact payment, private full-deck inspection, mandatory physical selection, observer-relative information, target movement, and shuffle topology.

The target's strategic usefulness is separate from whether a physical target must be selected.

## Limits

This adapter is intentionally specific to Computer Search semantics. It does not automatically generalize every unrestricted-search Item, attack, or Ability.

The target-selection policy is external. The transaction conditions on choosing to play Computer Search. If the decision to use the card depends on private K1-relevant state, the public action itself can be a signaling event.

## Next work

Compose this atomic transaction with a hand-size-sensitive continuation such as Dark Asset. That would quantify a complete path from exact payment and forced private target movement through downstream draw bandwidth.
