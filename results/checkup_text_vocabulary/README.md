# Historical Checkup terminology is a parser-normalization problem

## Question

Does the supplied Expanded card pool use one stable phrase for the between-turn
rules phase?

No. The vocabulary changes cleanly at the Sword & Shield era boundary.

Implementation: `tools/checkup_text_audit.py`  
Regression: `results/checkup_text_vocabulary/reproduce.py`

## Method

The audit:

1. loads `resources/sets/en.json`;
2. keeps sets released no earlier than Black & White base;
3. scans cards whose database legality metadata marks them Expanded-legal;
4. extracts Ability, attack, and rule text;
5. records text containing either `between turns` or `Pokémon Checkup`.

This is a corpus audit of the bundled database. It is not a substitute for the
repository's stronger per-card legality methodology.

## Corpus result

The current database yields:

- 106 print-text rows;
- 102 distinct card print IDs;
- 59 distinct relevant text strings;
- 62 rows using `between turns`;
- 44 rows using `Pokémon Checkup`;
- zero rows containing both phrases.

The latest relevant legacy wording is in Sun & Moon—Cosmic Eclipse
(`sm12`), released 2019/11/01.

The earliest relevant `Pokémon Checkup` wording is in Sword & Shield base
(`swsh1`), released 2020/02/07.

Within this corpus, the terminology transition is therefore cleanly bracketed
between those two sets.

## Why this matters

Literal-text parsers can accidentally split one timing family into separate
mechanics.

Examples already used elsewhere in this research thread show the same semantic
shape across the vocabulary boundary:

- Slumbering Forest: two-coin Asleep recovery using `between turns`;
- Slaking `sv2-162`: two-coin Asleep recovery using `during Pokémon Checkup`;
- Wela Volcano Park: suppress Burn recovery `between turns`;
- Centiskorch `swsh5-30`: suppress Burn recovery `during Pokémon Checkup`.

A card compiler should normalize historical wording to a canonical timing
concept before compiling effect semantics.

## Architectural consequence

A useful text-to-mechanics pipeline is:

`raw card wording -> era-aware timing normalization -> typed effect semantic -> state transition`.

The timing normalizer should preserve original text and print identity for
traceability while exposing a canonical `POKEMON_CHECKUP` timing label to
later layers.

This approach is safer than teaching every downstream mechanics kernel to
understand every historical synonym independently.

## Validation

The regression freezes the present corpus counts and transition bracket. If the
bundled card database changes, CI will signal that the vocabulary audit needs to
be recomputed rather than silently changing parser assumptions.

## Limits

The phrase `between turns` can appear in older effect text whose exact timing
semantics need card-specific interpretation. This result establishes a strong
historical vocabulary boundary; it does not claim that every sentence
containing the phrase compiles to the same transition.

Database `expanded: Legal` metadata is used as a search filter here. Formal
paper-Expanded legality remains a separate concern, as documented elsewhere in
the repository.
