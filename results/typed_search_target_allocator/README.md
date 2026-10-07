# Typed search-target allocator

## Question

How can compiled search effects use broad categories such as Trainer, Energy, or Pokémon while preserving physical card capacity?

A simple category-expansion map can count one physical target against several overlapping needs. This result adds exact target allocation.

Implementation: `tools/typed_search_target_allocator.py`  
Reproducer: `results/typed_search_target_allocator/reproduce.py`  
Validation: `.github/workflows/validate-typed-search-target-allocator.yml`

## Representation

The allocator separates search selectors, physical target groups, and strategic demand channels.

Physical target groups have explicit copy counts. When one search axis selects a copy, that copy leaves the remaining target pool and cannot be reused by another axis.

The trusted structural inheritance currently includes:

- Basic Pokémon -> Pokémon
- Evolution Pokémon -> Pokémon
- Stage 1 / Stage 2 Pokémon -> Evolution Pokémon
- Item / Pokémon Tool / Supporter / Stadium -> Trainer
- Basic Energy / Special Energy -> Energy

Pokémon type, Energy type, and Team Aqua / Team Magma identity are represented as orthogonal tags. Pokémon Tool does not inherit Item.

## Compiler coverage

The current conservative Trainer-search compiler emits 23 distinct output labels.

The typed layer supports 22. The sole deliberate exception is `Pokémon of different types`, because that wording creates a diversity constraint across several selected cards rather than a simple class-membership test.

## Findings

A single broad `Trainer card` search can retrieve an Item target or a Supporter target, but it cannot satisfy distinct Item and Supporter demands simultaneously.

Two overlapping axes, one Trainer and one Item, cannot both reuse one physical Item target. With two physical copies, both distinct demands become feasible.

Secret Box retains its genuine four-axis capacity. With one physical Item, Tool, Supporter, and Stadium target, the allocator finds the full four-output profile.

A one-card `Energy card` search can choose a Basic Energy or Special Energy target but cannot satisfy both distinct demands. A two-card Energy search can.

Dawn's Basic, Stage 1, and Stage 2 axes can satisfy all three stage demands when one target of each stage remains.

## Validation

GitHub Actions run `37554315033` passed on Python 3.13.

Its regression output confirmed:

- 23 compiler labels, 22 structurally supported;
- broad Trainer search cannot satisfy two distinct subtype demands with one unit;
- one physical target cannot be reused by overlapping search axes;
- two copies make the overlapping two-demand case feasible;
- Pokémon Tool does not count as Item;
- Secret Box can satisfy four distinct Trainer-subtype demands;
- one broad Energy search cannot satisfy Basic and Special Energy demands together;
- two Energy search units can;
- Dawn's three-stage profile is feasible.

## Integration boundary

`trainer_search_state_adapter.py` currently uses exact literal-label matching. The next step is to keep its lock, discard, play-condition, Supporter, Stadium, and target-zone checks while using this allocator for semantic target matching.

That integration can allow broad searches such as Rosa's Trainer search to satisfy narrower demands when real matching targets remain, without creating fictitious extra copies or output capacity.

## Limits

The allocator is deterministic and state-local. It does not yet handle the different-types diversity constraint, arbitrary card-text predicates, destination zones outside the current deck-search family, target strategic value, or dynamic semantic changes. Typed Energy matching relies on caller-supplied type tags.
