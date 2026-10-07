# Corpus-first inventory of opponent Energy-discard wording

## Question

Before compiling Energy-disruption effects, what wording actually appears in the
effectively legal bundled Expanded snapshot?

Implementation: tools/energy_disruption_text_catalog.py
Regression: results/energy_disruption_text_catalog/reproduce.py

## Method

The scanner uses the repository's effective legality classifier inside sets
marked Expanded-legal.

It retains Trainer rule bodies and attack texts that contain all four signals:
discard, Energy, opponent, and Pokémon. Text is whitespace-normalized, then
preserved verbatim in the catalog.

This intentionally over-collects. The purpose is to expose the corpus before a
semantic parser decides which rows are safe to compile.

## Validation

The regression requires a nonempty unique source inventory and confirms that a
known Hammer-family Energy-disruption card appears.

CI prints the complete normalized text-frequency table. That table will be used
to define exact semantic templates and to identify condition, coin-flip, target,
and quantity variants that require distinct transition fields.

## Why this step matters

A regex written from memory can silently merge strategically different effects,
such as:

- actor-chosen target versus Active-only target;
- any Energy versus Special Energy;
- deterministic discard versus coin-gated discard;
- one Energy versus several Energy;
- effects that add unrelated consequences.

The compiler should preserve those distinctions or refuse the text.

## Limits

The catalog is lexical, not semantic. A row appearing here does not mean it will
be accepted by the compiler.

Regional card-pool limits of the bundled English snapshot still apply.
