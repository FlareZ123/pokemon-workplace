# Full reacquisition matrix survives exact Trainer execution

## Question

The provenance-aware temporal ledger reports eight minimum-initial-filler values for the concrete Secret Box -> Guzma & Hala line: two endpoint profiles crossed with four reacquisition modes.

Do all eight abstract minima remain valid once actual deck copies, exact discard selections, Trainer resolving zones, and the Supporter quota are enforced by the canonical Trainer transaction layer?

Yes.

Reproducer: `results/reacquisition_transaction_matrix/reproduce.py`

## Method

This result reuses the repository's existing mechanical layers:

- `trainer_search_profile_compiler.py`;
- `typed_search_retrieval.py`;
- `search_zone_transition.py`;
- `discard_cost_witness.py`;
- `trainer_search_transaction.py`;
- `temporal_resource_ledger.py`.

The exact initial state contains Secret Box plus a variable number of filler cards in hand. The deck contains one Tag Call, one Guzma & Hala, two TM: Evolution, two Artazon, and two Jet Energy.

Secret Box always pays exactly three fillers, then searches one each of Tag Call, TM: Evolution, Guzma & Hala, and Artazon.

The second transaction plays that exact Guzma & Hala. Its discard selections are exhaustively enumerated over remaining filler, Tag Call, TM: Evolution, and Artazon. Its retrieval is varied across four modes:

- Jet Energy only;
- replacement TM: Evolution plus Jet Energy;
- replacement Artazon plus Jet Energy;
- replacement TM: Evolution plus replacement Artazon plus Jet Energy.

Because Jet Energy is a conditional output, every second transaction correctly pays the two-card optional discard and consumes the single ordinary Supporter quota.

For each mode and endpoint profile, the reproducer searches filler counts upward and accepts the first conserved transaction state satisfying the endpoint. The same scenario is independently solved through the abstract temporal ledger, and the two minima must agree.

## Result

The exact transaction matrix is:

| Endpoint requirement | No reacquisition | TM reacquisition | Artazon reacquisition | TM + Artazon reacquisition |
| --- | ---: | ---: | ---: | ---: |
| TM + Artazon + Jet | 4 | **3** | **3** | **3** |
| Tag Call + TM + Artazon + Jet | 5 | 4 | 4 | **3** |

All eight cells exactly match the prior temporal-resource result.

The canonical transaction layer therefore finds no hidden mechanical failure in the abstract minima. In every accepted line, card-class totals are conserved and Guzma & Hala consumes the Supporter action exactly once.

## Stronger interpretation

The earlier `reacquisition_transaction_bridge/` establishes one flagship three-filler witness. This matrix result is a broader falsification test.

It verifies both positive and negative boundaries:

- with no replacement route, the endpoint really needs more initial disposable stock;
- one replacement channel reduces the stock requirement only when the other required payload or Tag Call can still be retained;
- when Tag Call remains independently required, one reacquisition channel is insufficient to reach the three-filler floor;
- reacquiring both TM and Artazon restores the three-filler floor even under the larger endpoint.

This supports the temporal-ledger abstraction across the complete small scenario family rather than one hand-picked line.

## DCI consequence

The matrix makes discardability explicitly conditional on the set of live replacement channels and endpoint obligations.

A current TM or Artazon copy can be an exact legal discard in one branch and a mandatory retained payload in another state with the same current hand shape. The difference can come solely from what remains searchable in the deck and which endpoint resources still matter.

That is stronger than a static card-level discard score. A future discard policy should evaluate replacement reachability before assigning current copies high discardability.

## Limits

This remains a deterministic two-action family. It does not model opponent interaction, Prize uncertainty, deck-order beliefs, or whether the line is globally optimal.

The transaction target groups are built from the known conserved deck state. A larger planner still needs to discover the replacement route automatically rather than receiving the desired Guzma & Hala retrieval mode as an input.

## Next useful work

The natural next step is look-ahead discard policy: before paying a cost, enumerate reachable typed-search continuations and treat a required current copy as expendable only when the required class can be restored before its deadline.

That would turn the validated reacquisition phenomenon into a planner decision rule rather than a manually selected line.
