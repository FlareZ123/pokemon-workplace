# Aichi Bellelba Tag Call payload: paid G&H and late Stellar Wish

## Question

The original optional Aichi first-turn Tag Call search obtains up to
two more copies of Guzma & Hala (G&H) from the deck before G&H's
optional two-card discard. That Item can also take Bellelba &
Brycen-Man as a TAG TEAM Supporter. We added Bellelba as a second
physical output when zero or one additional G&H is searchable,
then compared the existing first-reset access objective under the
two allowed action sets.

This file reports a **uniform 500,000 raw-start diagnostic**. The
high-precision conditioned extension is documented separately in
[aichi_tagcall_conditional_payload](../aichi_tagcall_conditional_payload/).

Code: tools/aichi_tagcall_bellelba_payload.py.
SFT: [reproduce.py](reproduce.py).
Full fixed seed: [run.py](run.py).

## Physical action and ablations

After a normal Basic-valid opening, the player may take the
existing legal G&H route. When a naturally held extra Tag Call
can still be played before that Supporter, compare:

- baseline: the earlier option to fetch up to two more G&H copies;
- extended: fetch G&H first, then fill a remaining Tag Call output
  slot with Bellelba if it is searchable;
- protected Bellelba: the same extended physical search, with
  Bellelba excluded from legal G&H discard choices.

All paths conserve the held Tag Call Item, named searched cards,
remaining deck counts, and G&H's single Supporter use. The new
search reveals the physical remaining deck and hidden Prize
complement before the G&H discard.

The evaluation is restricted to pre-K1, unused late-Jirachi,
G&H-core-capable states in the existing Aichi simulator. The model
retains the previous conservative first-turn output protection for
no-prior-search states and endpoint-optimized post-search payment.

The score is the exact hypergeometric chance to access a specified
Ticket/Map Item immediately or via the **first** unused late Stellar
Wish after G&H. This score models a hypothetical rescue package
using neutral TechSlots, inherited from the parent research; it does
not measure match win rate or justify adding Bellelba to a different
deck.

## Uniform-sample observations

Fixed seed 20261010; 500,000 raw shuffled starts:

- 430,475 Basic-valid accepted starts;
- 23,184 late-Jirachi and pre-K1 setup states considered;
- 416 states with a legal additional Bellelba Tag Call output;
- among those 416, 400 had one extra G&H searchable and 16 had none.

The percentages in the following table are **contributions to
accepted-opening frequency from the 416 potential extended-route
states**, rather than the full initial setup success probability.
The two routing policies are paired on identical physical deals.

| First-reset objective | Package | G&H-only % accepted | With Bellelba % accepted | Paired gain pp (95% half-width) |
| --- | --- | ---: | ---: | ---: |
| Dual Stage 2 | One Ticket | 0.010762565% | 0.010913128% | +0.000150563 ± 0.000019903 |
| Dual Stage 2 | Two Tickets, one Map | 0.021099004% | 0.021348804% | **+0.000249800 ± 0.000033530** |
| Dual Stage 2 | Three Tickets, one Map | 0.028225848% | 0.028538653% | +0.000312806 ± 0.000042736 |
| Item lock | Two Tickets, one Map | 0.009257030% | 0.009388353% | +0.000131323 ± 0.000024362 |
| Item lock plus Pidgeot | Two Tickets, one Map | 0.005175697% | 0.005248287% | +0.000072590 ± 0.000018109 |

The full nine-metric results are recorded reproducibly in the
passing CI log.

**Surprising ablation:** the protected-Bellelba route produced the
same first-reset access values as the unrestricted Bellelba route
for every measured objective/package in this specific 500k sample.
The maximum paired unrestricted-minus-protected benefit was
**exactly zero**, and this was asserted by CI.

There is still a real material payment possibility: the separate
physical fixture gives a hand with held extra Tag Call and no other
disposable resources, one remaining G&H and Bellelba in deck,
with TM: Evolution and Jet Energy in deck. Fetching both TAG TEAM
Supporters provides the two distinct physical cards needed to
pay G&H's optional cost; fetching only G&H cannot make that payment.
This constructive state establishes the possibility, while the
sample's late-Ticket metric found no incremental score from
discarding Bellelba itself.

The positive first-reset effect in the tested sample arises from
**removing an extra card from the deck before the late top-five
Stellar Wish**. It increases the concentration of useful Item
targets in the reshuffled deck. This interpretation is supported
by exact equality under Bellelba discard protection in the
fixed-seed run; it is scoped to that sample and the modeled payoff.

## Validation

- Physical conservation fixtures cover G&H+Bellelba retrieval,
  Bellelba-only retrieval, two-G&H no-op equivalence, no-held-Tag
  refusal, and a two-card payment witness.
- Unconditional 10k raw-start smoke regression passed.
- 500k raw-start sample with a fixed seed and paired standard-error
  reporting passed.
- [10k smoke CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38061934105)
- [500k seeded CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38061934200)

## Interpretation and limitations

Bellelba is a singleton disruption Supporter in the published list.
Its potential value in future turns or matchups can exceed its worth
as discard fodder. The protected version retains it in hand, yet
the modeled early thinning advantage survives. Outside this exact
turn window, Tag Call's Item consumption and the later Supporter
cycle could impose strategic costs.

The original first-turn simulator assumes a permitted G&H Supporter
play, as on the first turn going second. It abstracts actual future
attacks, Tool attachments, multi-turn play and matchup decisions.
The same sample's post-search optimal choices are a state-informed
access estimate rather than a fully observed human policy.

The fixed-seed uniform sample sees only 416 candidate states.
A conditional, exactly reweighted sample of those rare targets
can narrow its uncertainty and examine whether the protected
and unrestricted policies ever differ under a broader set of
physical deals.
