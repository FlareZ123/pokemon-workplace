# Established precedence in a dynamic Ability-lock cycle

## Question

What happens when a previously one-way continuous suppression relationship
becomes reciprocal because the target later satisfies a new condition?

The official Garbotoxin / Cursed Land ruling shows that previous effective state
matters.

## Official evidence

The Japanese Pokemon Card Q&A considers Active Ting-Lu ex with **Cursed Land**
and an opposing Tool-attached Garbodor with **Garbotoxin**. When damage counters
are later placed on Garbodor, Cursed Land would ordinarily target damaged
non-ex Pokemon. The ruling says Garbotoxin does not disappear. At the moment the
damage is placed, Garbotoxin has already removed Ting-Lu ex's Ability, so Cursed
Land does not take effect against Garbodor.

Official Q&A search pages containing the ruling:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%87%E3%82%A3%E3%83%B3%E3%83%AB%E3%83%BCex&regulation_faq_main_item1=all

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%80%E3%82%B9%E3%83%88%E3%83%80%E3%82%B9

## State transition

Before Garbodor is damaged:

`Garbotoxin -> Cursed Land`

The dependency graph is acyclic, so Garbotoxin is active and Cursed Land is
suppressed.

After one damage counter is placed on Garbodor, a history-free graph becomes:

`Garbotoxin -> Cursed Land`

`Cursed Land -> Garbotoxin`

That snapshot alone is cyclic. The official ruling preserves the already
effective Garbotoxin source instead of treating the new reverse edge as a fresh
simultaneous fixed-point problem.

## Implementation

`tools/ability_lock_established_precedence.py` takes the previous resolved lock
state plus the new physical boards.

The implementation is intentionally conservative. It resolves a newly
reciprocal two-source cycle only when:

- the previous state had one active source;
- that source already suppressed the other source;
- the reverse edge is new;
- the current graph is exactly reciprocal;
- the profile pair is the verified `Garbotoxin -> Cursed Land` case.

Other newly cyclic states remain unresolved.

The single-source profile layer now includes all five bundled Ting-Lu ex Cursed
Land prints. Its targeting requires at least one damage counter and exempts
Pokemon ex.

## Regression

`reproduce.py` begins with undamaged Tool-attached Garbodor and Active
Ting-Lu ex. The ordinary dependency graph correctly resolves Garbotoxin as the
only active lock source.

The same Garbodor is then rebuilt with one damage counter while every other
mechanical fact remains unchanged. The history-free dependency graph reports a
two-node cycle. The established-precedence resolver preserves Garbotoxin,
matching the official ruling.

A separate target check confirms Cursed Land suppresses a damaged ordinary
Basic while leaving a damaged Pokemon ex unsuppressed.

## Implication

Continuous-effect resolution can require causal state from the immediately
preceding game state. A canonical simulator should preserve enough event
history to distinguish an established suppressor from a condition that has just
become true.

This result does not yet justify a general timestamp rule for all continuous
effects. Further official cases are needed before widening the verified profile
pair.
