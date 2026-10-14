# Multi-Prize pending identities retain correlated public evidence

## Question

Can an observer-model for Pokémon TCG preserve correlations between deck-top identity, remaining Prize cards and several simultaneously pending Prize cards, including when additional Prizes enter the queue before previous cards resolve?

The earlier [single-pending-card model](../pending_prize_public_reveal_belief/) retained one latent identity. The physical [Prize staging kernel](../../tools/prize_pending_take.py) already stages multiple physical cards but its original observer helper marginalizes removed identities immediately. That projection loses information if one of those cards is subsequently revealed in a public zone.

## Implementation

- [Batch joint posterior](../../tools/pending_prize_batch_belief.py) models `(top, remaining-Prizes, ordered-pending-identities)` per observer. It maintains the exact pending instance IDs alongside the grouped identities.
- [Physical-observer bridge](../../tools/physical_pending_prize_batch_bridge.py) stages the exact physical cards, conditions the actor on taken-card identity, preserves other observers' uncertainty, handles additional Prize insertion at the queue front, and advances physical and observer state together when the queue head enters hand, discard, or Lost Zone.
- [Regression](reproduce.py) exercises posterior conditioning, physical card conservation, nonmonotonic selection order, nested additional Prizes, errors, and a mixed private/public destination sequence.

## Explicit witness

Consider two equiprobable states with three Prize slots:

| Physical possibility | Top | Prize 0 | Prize 1 | Prize 2 |
| --- | --- | --- | --- | --- |
| Actual state | A | B | X | C |
| Other possibility | B | X | A | C |

Take positions 0 and 1 as one batch. The acting player sees B and X and infers top=A. The opponent retains P(top=A)=1/2.

Resolve the first taken Prize B into the actor's private hand. The opponent remains at 1/2. Resolve the second card X to the public Lost Zone. The opponent can now condition on X occupying the second taken slot, increasing P(top=A) to 1.

An immediate marginalization of both identities at staging would incorrectly leave the opponent at 1/2 after X becomes visible.

A second regression stages Prize positions in reverse order, then inserts an additional Prize at the front. It verifies that subsequent per-card destination observations update the correct latent identity and card instance.

## Rules and evidence boundary

The [official Lost Block plus Billowing Smoke ruling](../prize_destination_override_conflicts/) permits independent per-card destination choice on a two-Prize Knock Out after viewing both Prize identities. This implementation preserves the information required for such a choice. It does **not** implement arbitrary hidden-information policies or prove every possible multi-effect order.

Cards entering ordinary hand remain hidden to the opponent, while cards redirected to face-up discard or Lost Zone become publicly visible. The model currently supports those three destination zones only. It has no full-game winner policy and makes no claim about match win rates.

The physical bridge deliberately offers a new path instead of replacing the older `stage_prize_takes_with_observers` API. Existing callers retain their behavior; future simulator integration should select this path whenever a pending card might later become public.

## Validation

Run `python results/pending_prize_batch_correlation/reproduce.py`. The GitHub Actions workflow [validate-pending-prize-batch.yml](../../.github/workflows/validate-pending-prize-batch.yml) executes the same regression. No random sampling is involved: all probabilities derive from explicit enumerated support states.
