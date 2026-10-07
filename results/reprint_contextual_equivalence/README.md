# Reprint equivalence can change with the reachable format state space

## Question

Can an old official "legal reprint" compatibility label be treated as permanent evidence that two same-name texts are functionally identical?

## Answer

No. The current bundled paper Expanded card pool contains a concrete counterexample involving **Life Herb** and the historical **Pokémon-ex** class.

The official 2012 Modified-Legal Reprint List marks both `ex5-90` and `ex6-93` Life Herb as legal with **Reference Required: No**. Those printings say that Life Herb chooses one of your Pokémon **excluding Pokémon-ex**.

Later Life Herb text removes that exclusion. The current Expanded-legal `sm7-136` Life Herb can choose any of your Pokémon.

In the current repository snapshot, `me55c-108` Scizor ex is directly inside an Expanded-legal set, and its own rule text identifies it as the historical **Pokémon-ex** class. Therefore the target-set difference is reachable today:

- old Life Herb `ex5-90` / `ex6-93`: cannot choose that Scizor ex;
- current Life Herb `sm7-136`: can choose it.

The two texts consequently admit different actions in a current Expanded state.

## Why the 2012 label was still coherent

A reprint-compatibility decision is made inside a tournament format and card pool. A restriction can be strategically inert when no legal game object satisfies the excluded predicate.

This means a historical "Reference Required: No" row is evidence that the older printing was compatible with the legal format at that time. It does not prove a timeless, context-free semantic identity relation.

The distinction matters when old mechanics or card classes return. The 2026 Classic Collection reintroduces an old Pokémon-ex printing into the repository's Expanded universe, making the historical Life Herb exclusion observable again.

## Modeling consequence

Functional reprint resolution benefits from two layers:

1. **Text-level semantic comparison**, which determines where effects differ.
2. **Reachability analysis over the current format**, which determines whether the difference can ever affect a legal game state.

A useful formal view is observational equivalence over a format state space:

`card_A ≡_F card_B`

when, for every reachable legal state in format `F`, substituting one printing for the other preserves the legal actions and effect outcomes relevant to that card.

Under this representation, equivalence may change when the legal card pool changes.

This is consistent with the repository's broader finding that theoretical text access and executable game-state access are different objects. Here, a text predicate matters only when the format can produce an object satisfying it.

## Regression witness

`tools/reprint_contextual_equivalence.py` preserves one explicit witness:

- historical printings: `ex5-90`, `ex6-93`;
- current comparison printing: `sm7-136`;
- current Expanded witness object: `me55c-108` Scizor ex.

The tool asserts that:

- both historical Life Herb texts contain the Pokémon-ex exclusion;
- current Life Herb does not;
- Scizor ex is directly legal under the repository format model;
- Scizor ex's card text identifies the historical Pokémon-ex class.

This is a counterexample to promoting the complete 2012 no-reference list into a current equivalence overlay.

## Relationship to the semantic benchmark

[../reprint_semantic_benchmark/](../reprint_semantic_benchmark/) remains useful, but its 76 rows should be read as **historical compatibility cases**.

They can help locate wording families worth studying. They cannot all serve as unconditional positive labels for present-day functional identity.

The benchmark still contains strong current evidence from the Tournament Handbook:

- Copycat is an explicit positive pair;
- Rainbow Energy is an explicit negative pair.

Historical rows need an additional current-state reachability check before they can become current positive equivalence edges.

## Evidence classes

**Official historical evidence.** The 2012 Modified-Legal Reprint List marks the older Life Herb printings as requiring no reference.

**Card-text evidence.** The bundled card records preserve the historical Pokémon-ex exclusion, the current unrestricted Life Herb text, and the Pokémon-ex rule on Classic Collection Scizor ex.

**Format-data evidence.** The bundled set metadata marks the 30th Celebration Classic Collection as Expanded-legal.

**Modeling conclusion.** Reprint equivalence can be format-relative because a textual divergence can move between unreachable and reachable as the legal card pool changes.

## Sources

- 2012 Modified-Legal Reprint List: https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf
- Current Play! Pokémon Tournament Handbook reprint rule: https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/rules/play-pokemon-tournament-rules-handbook-10062023-en.pdf

## Reproduction

Run:

`python results/reprint_contextual_equivalence/reproduce.py`

The regression asserts two historical Life Herb source printings and one current Scizor ex witness.

## Limitations

This result proves one concrete failure of timeless historical compatibility. It does not establish a general algorithm for deciding whether every textual difference is reachable.

The repository legality model currently accepts the 30th Celebration Classic Collection through set metadata, with the broader legality work separately preserving provenance for set-level fallbacks. Any future correction to that format model should rerun this witness.

## Next work

A semantic resolver should emit both a normalized effect and its **divergence predicates**. For example, an old Life Herb comparison can expose the predicate `target is Pokémon-ex`. A format reachability layer can then ask whether any legal state can satisfy that predicate before deciding equivalence.
