# Source-aware KO certainty without global order enumeration

## Question

Can a simulator identify whether an unresolved official effect-order chooser changes the terminal material state, while avoiding enumeration of all combinations of independent effect order choices?

Yes, for the repository's fixed pending-Knock-Out and destination-only routing semantics. The new `tools/ko_authority_local_certificate.py` composes two proven interfaces:

- `source_order_chooser.assess_concrete_ordering_player` retains the selected source claims, identified chooser if any, and disagreement or missing-context status;
- `ko_component_state_invariance.certify_component_ko_invariance` determines terminal-state invariance from independent local conflict-group histograms.

The result preserves both answers independently. It is a **decision-only** API: if the physical state is order-sensitive, it returns no selected terminal state and deliberately omits counts of every distinct global terminal state. The original [full authority-neutral projection](../ko_authority_neutral_projection/) remains available for cases where complete endpoint enumeration is necessary.

## Official card-text witness

Under Pokémon Japan's current official Q&A for **Lost City versus Tyranitar-GX Lost Out**, the KO'd Pokémon's owner chooses their order. February 2026 TPCi Professor guidance instead describes current-turn-player choice for multiple during-turn Knock Out effects. The repository keeps those source scopes separate.

When attacking Tyranitar-GX Knocks Out defending Lapras under Lost City, the returned source assessment is a conflict between attacker and defender in both of these fixture states:

- With **no attached Energy**, Lost City-first and Lost Out-first both send the same Lapras into Lost Zone. The certificate returns an exact conserved terminal state while preserving `AUTHORITY_CONFLICT`.
- With **one or more attached Basic Water Energy**, Lost City-first discards attachments and Lost Out-first sends them into Lost Zone. The certificate returns `invariant=False`, no terminal state, and the still-unresolved source dispute.

The regression checks zero through four attached Basic Water copies against the earlier exhaustive physical projection, including full state equality in the invariant case and exact total labeled order counts.

## Large synthetic test

For the earlier 20-effect, ten-independent-pair fixture, the fast certificate discovers that each two-effect group independently changes its local final zone histogram. It examines **20 component-local destination outcomes** to prove that the overall terminal state is order-sensitive. This replaces the need to construct the fixture's 1,024 global instance-level routes merely to answer a yes/no question. It still records exactly `20!` candidate total effect orders.

The synthetic effect programs are scalability inputs, with no claim that these twenty simultaneous triggers arise from printed cards.

## Boundary

The certificate assumes the downstream game-state mutation consists solely of the specified destination-only KO disposal. Rules-source disagreement and actual legal order authorization remain unresolved where their evidence conflicts. Hidden-information changes, evolving trigger sets, Prize-taking, surviving board effects, and strategic payoffs remain separate layers. If any such effect changes a terminal state beyond card-zone routing, local histogram invariance alone is insufficient.

## Reproduction

`python results/ko_authority_local_certificate/reproduce.py` tests the official Lost City / Lost Out fixture, source-status preservation, exact agreement with exhaustive state projection and synthetic ten-component stress. Companion workflow: `.github/workflows/validate-ko-authority-local-certificate.yml`.
