# Typed-Energy no-Retreat-Cost Abilities: 27 exact prints

## Scope and source audit

The supplied English card corpus contains **27 Expanded-labeled
print IDs** whose printed Abilities grant no Retreat Cost conditioned
on having Energy of a *particular type* attached.

`source_audit.py` scans the entire bundled English corpus,
recognizes `<type> Energy attached` in no-cost Ability text,
and matches the resulting IDs, card names, Ability names, Energy
symbols and self/team scopes against
`tools/retreat_typed_energy_no_cost.py`.

| Ability scope | Prints | Families and requirements |
| --- | ---: | --- |
| The source's own Pokémon | 14 | Royal Garden (Grass), Aqua Lift (Water), Rock Hiding (Fighting), Frubbles (Water), Ice Float (Water), Voltaic Float (Lightning), Flare Float (Fire), Mist Float (Psychic), Explosive Heat Dash (Fire) |
| All friendly qualifying Pokémon | 13 | Dark Cloak (Darkness), Thunderclap Zone (Lightning), Lunar Zone (Psychic), Metal Bridge (Metal), Aqua Tube (Water) |

All source IDs, including reprints, are stored explicitly. A source
must be in play, have the exact verified card name and print ID, and
have its Ability enabled. A self-effect applies only if the source
is the current Active. The team effects may apply from a friendly
Bench source. Opposing sources never provide friendly Aura bonuses.

This registry extends the earlier
[low-energy threshold](../retreat_low_energy_no_cost/)
and [conditional self](../retreat_conditional_self_free_cost/)
free-Retreat source families.

## Energy *type* versus Energy *quantity*

The existing Retreat payment model normalizes certain Special
Energy cards to `C` symbols for unit-counting, even when their
printed effect provides every type of Energy. That generic
normalization is correct for Retreat **payment amounts** but loses
information required to trigger typed free-Retreat Abilities.

The new `provides_required_energy_type` helper restores
known **exact-print** Special Energy type behavior independently
of generic payment units:

- Rainbow, Aurora and Legacy Energy supply every Energy type.
- Prism Energy supplies every type while attached to a Basic Pokémon.
- Double Dragon Energy supplies every type on a Dragon Pokémon.
- Fusion Strike Energy supplies every type on an eligible Fusion Strike Pokémon.
- Unit Energy supplies its printed three respective Energy types.
- Counter Energy supplies every type when its player is behind
  on Prize cards and the holder is not Pokémon-GX or Pokémon-EX.
- Reversal Energy supplies every type when the player is behind
  and the holder is an Evolution Pokémon without a Rule Box.
- Luminous Energy supplies every type when there are no *other
  Special Energy cards* attached. Other Basic Energy cards are allowed.

Other physical Energy attachments can supply an explicitly represented
symbol from their current `EnergyAttachment.units` snapshot.
This is a **source-specific, conservative typed-provider subset**;
the helper does not claim complete semantics for every possible
Special Energy in Expanded. Card-print snapshots and recognized
providers must be materialized accurately by upstream game state.
Unsupported conditional provider modes are not silently asserted
to provide an arbitrary requested type.

## Physical prize-dependent counterexample

Construct a Stage 1 Active Pokémon with one Reversal Energy
(`sv2-192`), and one friendly Benched Darkrai-EX
(`bw5-63`, Dark Cloak). A second Pivot is Benched.
Galar Mine (`swsh2-160`) adds two to the printed Retreat Cost
of two, yielding four unless a no-cost Ability is active.

| Public Prize counts (own, opponent) | Reversal's current units | Reversal provides Darkness | Dark Cloak effective Retreat Cost |
| --- | ---: | --- | ---: |
| (6, 5): behind | 3 | Yes | 0 |
| (5, 5): tied | 1 | No | 4 |

The existing physical Retreat action enumerator, dynamic Special
Energy normalization, current type predicate, and board-derived
Aura modifier agree: behind yields two executable zero-payment
Retreat-to-Bench choices, while tied yields none with only that
one attached Reversal Energy. Suppressing Darkrai's Ability
removes both free-Retreat choices even when Reversal is active.

The three units from Reversal remain generic `C` in the payment
kernel; the type predicate uses the exact printed Special Energy
rule plus public Prize state. Thus the successful path exercises
the distinction between count and type in the actual integrated
Retreat executor.

## Tests and limitations

`reproduce.py` checks all 27 source names/scopes/types, negative
type and Ability-suppression controls, opponent-versus-friendly
Aura ownership, context-dependent provider types, and physical
zero-payment Retreat action frontiers. `source_audit.py` provides
an independent complete corpus scan.

The dedicated
`.github/workflows/validate-retreat-typed-energy-no-cost.yml`
also reruns prior dynamic Special Energy, low-energy, conditional
free-cost, and board-derived Retreat tests.
[CI run 38281119342 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38281119342).

The exact scenario shows deterministic legal-action feasibility.
No deck opening frequency, metagame prevalence, or match-winning
strength is inferred. The research concerns **paper Expanded**,
using the bundled English print snapshot; regional print acceptance
and current tournament-ban status require separate adjudication.
