# Conditional Monte Carlo: Bellelba's second TAG TEAM search output

## Research question

In the Aichi Vileplume first-turn access model, a supplemental
naturally held Tag Call is currently represented as retrieving only
additional Guzma & Hala (G&H). The English card text permits searching
another TAG TEAM Supporter, including Bellelba & Brycen-Man.

The exact card-count result at
[aichi_tagcall_second_slot](../aichi_tagcall_second_slot/)
shows that Bellelba can supply one more physical Tag Call output when
zero or one extra G&H is searchable. Does that opportunity produce
additional *first-reset access* through a legal G&H payment, or does
its modeled value primarily arise from removing a card from the
remaining deck?

This experiment extends the existing agent4 Aichi first-turn
model with a named physical Bellelba fetch, a
protected-singleton sensitivity, and a high-efficiency conditional
sampling scheme.

Implementation:
tools/aichi_tagcall_bellelba_payload.py and
tools/aichi_tagcall_conditional_payload.py.

Small SFT: [reproduce.py](reproduce.py).
Fixed-seed conditional experiment: [run.py](run.py).

## Card-text and state model

The underlying Aichi list contains G&H4, Tag Call4 and Bellelba1.
The included Cosmic Eclipse cards make both G&H and Bellelba TAG TEAM
Supporters, while Tag Call is an Item searching up to two TAG TEAM
cards. Therefore:

- A supplemental Tag Call with two G&H remaining may fetch two G&H.
- With one extra G&H remaining and Bellelba in deck, it can fetch
  **G&H plus Bellelba**.
- With no extra G&H remaining and Bellelba in deck, it can fetch
  **Bellelba alone**.

The previously selected G&H used this turn is already represented as
consumed in the Aichi Prepared state. Tag Call moves each fetched
card physically from the remaining deck into the modeled hand before
the optional G&H two-card discard payment. The extra TAG TEAM
Supporter does not grant an additional ordinary Supporter play.

The comparison takes the maximum available first-reset access from:

1. A regular route with a conservative guard preserving already-held
   TM: Evolution, Jet Energy and Artazon, because payment occurs
   before full-deck knowledge.
2. The prior G&H-only supplemental Tag Call route, whose search
   grants deck/Prize knowledge before the payment.
3. The new G&H/Bellelba supplemental Tag Call route, also granting
   prepayment knowledge.

The new route's payment selection is made after searching, and may
therefore depend on revealed Prize composition. The player can always
decline the extra route.

A secondary ablation prohibits discarding Bellelba from the expanded
route. This tests whether its mere physical extraction from the deck
can matter to a late Stellar Wish even when the singleton remains
strategically protected.

The downstream score is the probability of having the relevant
Ticket or Map Item immediately, or finding it using an unused late
Jirachi Stellar Wish after G&H. Its top-five probability is exact
hypergeometric within each simulated state.

This score remains an optimistic, restricted access proxy:
other effects, post-first-turn strategic utility, and the broader
Vileplume battle are unmodeled.

## Why condition on rare event strata?

The exact natural-opening census proves that an added Bellelba
search output is possible only in these two strata:

| Searchable extra G&H | Bellelba searchable | Accepted-start mass |
| ---: | --- | ---: |
| 0 | Yes | 0.005531280123% |
| 1 | Yes | 0.102471870248% |

Uniform 500,000-start sampling visits this combined event only a few
hundred times. A conditional simulator samples it directly and
reweights the resulting average by its *exact combinatorial mass*.

For each stratum g, sample the seven non-Jirachi visible cards using
the exact conditional weight for k held G&H and t held Tag Call:

\[
W_g(k,t)=
\binom4k\binom4t\binom{50}{7-k-t}
\binom{4-k}{4-k-g}
\binom{47+k}{6-(4-k-g)}.
\]

Once (k,t) is drawn using integer proportional weights:

1. Choose the k G&H, t Tag Call and 7-k-t other physical cards
   uniformly, then assign six to the opener with Jirachi and the
   seventh to the normal turn draw.
2. Prize exactly 4-k-g of the remaining G&H copies, none of the
   Bellelba singleton, and fill the six Prizes uniformly from
   non-G&H, non-Bellelba cards.
3. Uniformly permute the remaining physical cards into the draw deck,
   retaining the first five as the potential early Stellar Wish
   observation.
4. Apply the same Aichi preparer, G&H discard frontier, setup
   endpoint and late-Stellar Wish calculation to each paired policy.

This is a conditional sample of an otherwise random physical deck
permutation. All 60 card instances remain distinct and are conserved.
The stratum masses are calculated by exact Fraction arithmetic,
independently checked against the full target-count census.

The output is

\[
\Pr(g=0,B=1\mid\mathrm{accepted})\,E[\Delta\mid g=0]
+\Pr(g=1,B=1\mid\mathrm{accepted})\,E[\Delta\mid g=1],
\]

where \(\Delta\) is the paired positive change in late first-reset
access from allowing the new search. The 95% uncertainty interval
uses the independent sample variances within the two strata.

## Checks

The SFT tests physical card conservation, target counts, Jirachi
opening placement, correct six-Prize and natural-draw positions,
presence of the held G&H/Tag Call, and the exact relation between
integer category weights and the independent 60-card probability
census.

A smaller unconditional 500,000-start run at
[results/aichi_tagcall_bellelba_payload](../aichi_tagcall_bellelba_payload/)
provides a separately seeded paired estimate that the conditional
result can be compared against.

See the follow-up quantitative summary below after the large
conditional experiment is validated.

## Limitations

The original G&H search/action model is still an idealized
first-turn planner. It uses endpoint-conditioned payment choices after
full searches and a conservative guard before full searches; the
guard is a proxy rather than the uniquely optimal genuine K0 policy.

Bellelba's value on future turns and against control matchups is
absent from the access metric. The protected-Bellelba ablation
recognizes that a singleton can have low discardability, but cannot
quantify its actual gameplay opportunity cost. The experiment
measures a probabilistic access difference, not tournament win rate.
