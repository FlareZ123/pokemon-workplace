# Exact printed-HP gate for direct-to-Bench Item search

## Question

Does the existing exact direct-Bench Trainer transaction represent Buddy-Buddy
Poffin safely when its searchable Pokémon are restricted by printed HP?

**Yes, with a separate card-grounded selector gate.** The generic physical
transaction can materialize Basic Pokémon into in-play Bench objects, but the
existing `Basic Pokémon` target lattice does not encode an HP ceiling.

Implementation: `tools/hp_bounded_direct_bench_transaction.py`  
Regression: `results/hp_bounded_direct_bench_transaction/reproduce.py`  
CI: `.github/workflows/validate-hp-bounded-direct-bench.yml`

## Source and compiler boundary

The bundled English effectively legal Expanded pool contains five literal
Buddy-Buddy Poffin prints: `sv5-144`, `sv6-223`, `sv8pt5-101`,
`me1-167` and `me2pt5-184`. All use the search instruction:

> Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them
> onto your Bench. Then, shuffle your deck.

The conservative compiler accepts Item prints only when that direct-Bench
search body is the entire operational effect. It preserves the exact Item
print, a two-Pokémon maximum and the inclusive **70 printed HP** ceiling.

The profile projects to the existing generic Basic-target transaction only
*after* the HP adapter filters and authenticates the target universe. This
prevents the generic search allocator from treating ineligible high-HP Basics
as valid Poffin search candidates.

## Trusted print identity

The adapter requires both existing resource-derived indexes:

- `pokemon_board_metadata_by_id`: legal Pokémon print, name, Basic tag,
  retreat cost, and evolution metadata;
- `build_pokemon_card_profile_index`: legal print ID, name and printed HP.

It verifies every declared target's exact print class and full metadata against
the trusted indexes. The declared search candidate universe must consist
entirely of eligible prints. This prevents a caller from changing a name, tag
or HP label to smuggle an 80-HP Pokémon into a 70-HP search.

The HP bound applies to the **printed card**, rather than modified in-play HP,
and the target must be a Basic Pokémon.

## Physical regression

The deterministic reproducer checks three real exact prints:

| Print | Pokémon | Printed HP | Poffin result |
| --- | --- | ---: | --- |
| `sm11-90` | Elgyem | 60 | Eligible |
| `sv1-13` | Sprigatito | 70 | Eligible at the inclusive boundary |
| `me55-93` | Murkrow | 80 | Rejected |

With three occupied Bench slots, Poffin can move Elgyem and Sprigatito in a
single transaction, filling the final two spaces. With four occupied Bench
slots it can place only one. With a full Bench it cannot be used.

In the successful two-target transition:

- the exact Poffin print is discarded from hand;
- the two selected deck copies become separate in-play Pokémon objects;
- each new Pokémon is ineligible for immediate ordinary evolution;
- neither search target visits hand;
- the private `direct_bench_selected` staging zone is consumed;
- the existing Item turn budget is unchanged;
- whole-ledger physical card totals remain conserved.

Negative tests also reject stale deck-target counts, forged target metadata,
a mismatched played Item print and ineligible 80-HP targets.

## Strategic consequence

The HP gate affects the space of **legal early setup lines**, including
whether two separate Basic roles can both be fetched with one Item. Earlier
[Beheeyem/Poffin eligibility research](../beheeyem_poffin_eligibility/)
shows that search eligibility can reverse preferred first-turn Item allocations
in a deliberately narrow two-Basic event.

This implementation provides executable source-card semantics for testing
those setup decisions against physical board constraints.

## Limitations

This transaction includes exact Item lifecycle and physical placement, but
does not itself perform a deck shuffle, update observer beliefs, or model
opponent Item lock and potential printed-HP changing effects in other zones.
The existing `direct_bench_hidden_state_bridge.py` supplies a separate
single- and multi-target observer-belief layer. A future wrapper can compose
that bridge with this HP gate.

The adapter is intentionally a conservative **literal Item semantic island**,
not a claim that every HP-constrained search effect or every Buddy-Buddy
Poffin matchup is completely simulated. No game-win percentage follows from
this mechanical regression.
