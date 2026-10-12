# Distinguish Tag Call's physical deck thinning from prepayment Prize information

## Why this matters

The published 2026 Aichi Vileplume-control list carries four Guzma & Hala (G&H) and four Tag Call. G&H's optional two-card discard is committed **before its own search**; Tag Call is an Item that can perform a deck search **before** that payment. An optimistic K1 solver may ascribe all downstream improvement to learning Prize identities, even though fetching TAG TEAM Supporters actually removes cards from the deck and increases the odds of a later Jirachi Stellar Wish revealing a desired Item.

This exact calculation separates the contributions under one explicit conditional physical model.

## Fixed state and exact Prize classes

- A seven-card hand plus one normal draw is already observed. One G&H, one Tag Call, one TM: Evolution, one Jet Energy, and two otherwise expendable resources are assumed to be held. A Jirachi is eligible for one unused post-G&H Stellar Wish. This is a *hypothetical conditional window*, not a deck-wide opening frequency.
- Unseen: `U=52` cards, including 3 more G&H, Artazon, spare TM, spare Jet, one Ticket-role Item, and 45 fillers. Six Prizes are uniformly selected from those cards.
- When available, Tag Call retrieves exactly two additional G&H copies, or one if only one survives Prizes, and thereby reveals the entire deck (K1). It searches and shuffles before the held G&H is played.
- The result conditions on at least one additional G&H being searchable, an exact **1104/1105** of the fixed initial hidden pool. The remaining 1/1105 world class is excluded to avoid making unsupported claims about an empty-target Tag Call play.
- G&H always searches Artazon if present. With an optional two-card discard it also searches spare TM and spare Jet if present. The discretionary payment incurs invented future resource value `lambda=10/2499`; the same penalty applies to both models. G&H search targets may adapt after its play to physical deck presence.
- The eventual unused Wish views five randomly shuffled remaining cards. The score is **P(Ticket seen) minus the discretionary payment penalty**. This scalar is an illustrative decision utility, not a game-winning probability.

Enumerate the four named Prize flags and how many of three additional G&H copies are Prized, with exact weight `C(3,j) C(45,P-k-j) / C(52,P)`, where `k` denotes the number of distinguished cards Prized. For each world, removing the fetched G&H decreases the later Wish deck denominator. All fractions below are conditional on the successful Tag Call availability event.

## Main result

| Decision window | Exact conditional score | Score as percentage |
| --- | ---: | ---: |
| No Tag Call, optimal K0 payment | `5195/52992` | **9.803366546%** |
| No Tag Call, hypothetical free full K1 | `2406750833/24355993704` | 9.881554669% |
| Tag Call removes G&H, payment still constrained to one K0 action | `17788265/172890816` | **10.288727540%** |
| Tag Call removes G&H and reveals K1 before payment | `3511495835/33886599936` | **10.362490901%** |

The improvement attributed to making the Tag Call material search, **while holding the prepayment decision K0-constrained**, is `10069735/2074689792` or **+0.485360994 percentage points**.

Learning the remaining full deck after that same material search provides an additional `8331965/11295533312` or **+0.073763361 percentage points**.

The total gain, with zero external Tag Call opportunity cost, is `142101175/25414949952` or **+0.559124355 percentage points** relative to the no-Tag-Call K0 benchmark. Thus most of this deliberately limited objective's apparent preview benefit derives from **physical deck thinning**. The pure information increment is only the smaller residual.

## Action-cost threshold and limitations

Tag Call is a finite physical Item and the extra G&H cards may be valuable later as discard, Supporter access, or resource recovery. The calculation currently prices **only G&H's optional discard**, not consuming Tag Call or removing future Supporters from the deck. If an analyst assigns Tag Call a separate scalar utility cost `tau`, then this particular simplified model favors the preview route only if `tau < 142101175/25414949952`. This is a **synthetic** utility threshold. It is not a recommended strategic price for an Item.

The model assumes fixed hand material, held first TM/Jet, a single remaining Ticket target, Wish eligibility, no Item lock, and immediate G&H access. It omits full game state, alternate Tag Call targets (Bellelba & Brycen-Man), TAG TEAM discard values, real Aichi opener frequencies, draw-engine contention, Stadium playing constraints, and matchup utility. It therefore does not establish actual benefit for a tournament list or justify any deck slot modification.

## Reproduction

The [grouped exact engine](../../tools/gnh_tagcall_material_information.py) implements at most sixteen named configurations multiplied by three G&H-Prize counts. The [single-file independent test](reproduce.py) instead explicitly enumerates labeled physical Prize deals and every Wish subset in smaller decks, checking all four benchmark scores plus G&H availability mass. It confirms the two increments sum exactly to the total and reproduces the stated 52-card rational outputs. [Manual Windows CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292661262).

**Next use:** carry actual Tag Call alternatives, protected future Supporter value and K0-visible hand classes into the Aichi turn policy. Keep observational information provenance explicit.
