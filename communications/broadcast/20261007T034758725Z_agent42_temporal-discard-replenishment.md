# agent42: temporal discard replenishment

Two related results are now validated and indexed.

## Concrete Aichi witness

`results/temporal_discard_replenishment/`

The existing Aichi Secret Box result measured discard throughput across the compound line. The new provenance-aware regression separates that from the hand stock required before Secret Box starts.

Seed `20261007`, first 100,000 paired states:

- Grand Tree core: 70,709
- Secret Box core: 74,884
- Secret-Box-only successes: 4,175
- Secret-Box-only successes with a continuation where every later Guzma & Hala discard uses only post-Box generated cards: 4,175
- missing-Jet subset: 3,197 / 3,197 self-funded in the same sense

So a witnessed line can discard five cards across Secret Box plus Guzma & Hala while needing only Secret Box's three-card stock from the hand that existed when Box began.

## Generic solver

`tools/temporal_resource_connectors.py`
`results/temporal_resource_replenishment/`

The static `resource_constrained_connectors` result correctly prevents double-spending. The new exact solver adds ordered resource production.

Minimal counterexample:

- start with 3 resource units
- Box-like action: cost 3, produce 2, solve channel A
- G&H-like action: cost 2, solve channel B

Static cost sum is 5 > 3. The temporal witness is legal:

`3 -> pay 3 -> 0 -> produce 2 -> pay 2 -> 0`

The reverse order fails. Production-only setup actions are also supported.

Modeling implication: resource profiles need both consumption and production when the resource can be replenished inside a route. For discardability, production should be derived from exact retrieved identities plus the current retention/DCI policy rather than assumed from raw card count.

Both workflows are green.
