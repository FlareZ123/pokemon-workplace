# Official rule-change precedence for simultaneous Knock Outs

## Question

How should research treat a still-live official FAQ that contradicts a newer
official rules document?

The concrete case is simultaneous Knock Out-trigger ordering.

## Conflicting official evidence

The Japanese official FAQ entry with FAQ ID 8833 asks about Manaphy with
Last Wish and Team Plasma Weezing with Aftermath being Knocked Out at the same
time by the opponent's attack. It says the owner of Manaphy and Weezing chooses
which effect resolves first.

Source:
https://www.pokemon-card.com/rules/faq/details.php?id=8833

The current Advanced Player's Rulebook v3.4 says that when several Pokemon are
Knocked Out at the same time and several effects activate in KO step 2, the
player whose turn is currently being played decides their order.

This is a real chooser difference in the FAQ's scenario because the opponent is
the player taking the turn while the Knocked Out Pokemon share the other owner.

## Dated rule change resolves the conflict

Pokemon Japan published an Advanced Player's Rulebook update notice on
2025-08-01.

Source:
https://www.pokemon-card.com/info/005161.html

For E-04, the notice explicitly says the simultaneous-KO processing order was
changed so the player taking the current turn can choose the order. The notice
also states that the update and ruling changes apply from 2025-08-01.

The current v3.4 rulebook therefore represents the effective rule for this
scope. FAQ 8833 remains useful as historical evidence of the previous rule.

## Repository consequence

Official-domain provenance by itself is insufficient for rules research.

A rules evidence record needs at least:

- scope;
- source;
- version or effective date when available;
- whether a later official change supersedes it;
- the chooser or mechanical claim;
- enough scenario detail to detect whether two claims truly conflict.

Searchable FAQ pages should not automatically override a newer rules manual.
Likewise, an old FAQ should not be deleted from the evidence base because it can
explain older tournament reports, legacy simulations, or apparent contradictions.

## Regression

`evidence.json` records the legacy FAQ claim, the dated rule-change notice, and
the current rulebook claim.

`reproduce.py` independently audits the bundled v3.4 rulebook and verifies that
its multi-Pokemon KO authority is `current_turn_player`, matching the
2025-08-01 change notice.

The regression intentionally preserves the old owner-choice claim as
`superseded_by_2025_rule_change`.

## Finding

Rules evidence is versioned state.

For current paper Expanded analysis, the multi-Pokemon KO trigger-order rule is:

`current-turn player chooses`

The still-live owner-choice FAQ is stale for this scope after 2025-08-01.

This also changes how apparent source contradictions should be handled. The
first question is whether a later official rule-change notice establishes an
effective-date boundary. Only unresolved same-version conflicts should remain as
live ambiguity.

## Limits

This result resolves the generic simultaneous-multi-KO ordering scope only.

It does not establish precedence for every card-specific ordering ruling. A
specific ruling can describe a narrower topology that is outside the changed
generic scope. Such cases still need their own applicability analysis.
