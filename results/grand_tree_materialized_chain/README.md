# Grand Tree evolution search is constrained by physical deck zones

## Question

The existing Grand Tree chain adapter proves that a single Stadium effect can
evolve Bulbasaur -> Ivysaur -> Venusaur. But Grand Tree obtains both evolution
cards by searching the **deck**. What changes if one of those cards is Prized
and cannot be searched?

## Finding

The chain requires Stage 1 to exist in the searchable deck. Stage 2 is an
optional follow-through, so its absence does not invalidate a legal Stage 1
evolution. This is distinct from treating the complete Stage 1 + Stage 2
chain as an all-or-nothing line.

A concrete controlled physical-zone witness:

| Available zones | Stage 1 result | Stage 2 result |
| --- | --- | --- |
| Ivysaur in deck, Venusaur in deck | Yes | Yes |
| Ivysaur in deck, Venusaur Prized | Yes | No |
| Ivysaur Prized, Venusaur in deck | No | No |

Cards: Grand Tree `sv7-136`, Bulbasaur `bw5-1`, Ivysaur `bw5-2`,
Venusaur `bw5-3`. This is a zone-availability test conditional on these
specific copies and on otherwise legal Stadium activation/target timing.
There may be other legal search targets or recovery routes in a full deck.

## Representation

`tools/grand_tree_materialized_chain.py` composes:

- `grand_tree_chain_execution` for both evolution stages within one source;
- `identity_materialization` to turn exchangeable deck card counts into
  stable physical instances bound to the Pokémon's evolution stack;
- `validate_board_position_stack_bindings` for board/ledger agreement;
- `assert_conserved` to prove total card-class counts are unchanged.

Both evolution cards are required to be materialized from the **deck**.
The initial Bulbasaur is a preexisting in-play materialized card.
The two chosen evolution cards are bound to the same persistent board object.
The Stadium instance-use allowance is marked exactly once after a successful
chain. All staged state is immutable and returned only after validation.

If a requested Stage 2 copy is Prized, the full proposed two-stage transition
returns no result without spending the Stadium instance. The caller can make
the valid optional decision to take Stage 1 alone. If Stage 1 is Prized, both
proposed chains fail.

## Reproduction

`python results/grand_tree_materialized_chain/reproduce.py`

The reproducer validates the three zone cases above, exact stack membership,
correct in-play card-instance bindings, total conservation, once-per-instance
Stadium effect usage, no additional Stadium-play charge, and failed
candidate rollback.

## Limits

The input deck-zone inventory and requested card identities are known to the
caller. This is a conditional deterministic witness, not a complete hidden
information policy or a proof about typical setup probabilities. The class
inventory identifies only the cards used in this test; the caller is
responsible for real card-print identity/eligibility and other deck copies.

Actual card selection from a shuffled deck, information acquired during the
search, post-search shuffling and topdeck distribution, removal/replay of
Stadiums, and other game-state restrictions remain in separate layers.

A future layer should combine this physical zone transaction with the
repository's K0/K1 search-information model, then evaluate when a player
should elect the optional Stage 2 step.

## Confidence

High for the represented identity-conservation and search-zone constraints,
subject to the explicitly controlled physical availability assumptions.
