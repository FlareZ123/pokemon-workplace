# Effect-order authority changed on 2025-08-01

## Question

Can historical official rulings be used directly for current paper Expanded
timing?

Only after checking the applicable rules version.

## Three coordinated rule changes

Pokemon Japan's 2025-08-01 Advanced Player's Rulebook update notice explicitly
changes three ordering families:

| Case | Rulebook v3.0 | Rulebook v3.4 |
| --- | --- | --- |
| several Pokemon are Knocked Out simultaneously and KO-step effects activate | owner of the Knocked Out Pokemon | current-turn player |
| several effects activate from Energy attachment | owner of the Pokemon receiving the effects | current-turn player |
| several effects apply during Pokemon Checkup | owner of the Pokemon receiving the effects | player whose turn would be next |

Sources:

- v3.0: https://www.pokemon-card.com/info/2022/05/images/Ruleguide_ver3.pdf
- 2025 change notice: https://www.pokemon-card.com/info/005161.html
- v3.4: https://www.pokemon-card.com/assets/document/advanced_manual.pdf

The change notice states that the updated rulings apply from 2025-08-01.

## A still-live stale FAQ witness

FAQ ID 8833 remains searchable on the official Japanese site. It asks about
Manaphy with Last Wish and Team Plasma Weezing with Aftermath being Knocked Out
simultaneously by the opponent's attack. The answer gives the ordering choice to
the owner of those Knocked Out Pokemon.

Source:
https://www.pokemon-card.com/rules/faq/details.php?id=8833

That answer matches the old v3.0 E-04 rule exactly. It conflicts with v3.4 in
the FAQ scenario because the opponent is taking the turn.

The 2025 dated change resolves the conflict for current play. The FAQ remains
historically useful, while its generic E-04 ordering conclusion is superseded.

## Repository consequence

Rules evidence is versioned state.

A useful evidence record needs the rule scope, source, version or effective date,
chooser role, and supersession relationship. An official-domain URL alone does
not establish that its ruling is current.

This matters especially in Expanded research because old cards naturally lead
searches toward old FAQ entries. Those pages can describe the rules that applied
when the cards were released while remaining accessible after a later global
rules change.

## Regression

`evidence.json` records the three v3.0 to v3.4 chooser migrations plus the
stale FAQ witness.

`reproduce.py` audits the bundled v3.4 manual and verifies the current chooser
roles for E-04, E-07, and E-08. It also checks that FAQ 8833's owner-choice role
matches the stored legacy E-04 role rather than the current one.

## Finding

Current paper Expanded timing should use the v3.4 chooser roles for these three
generic scopes from 2025-08-01 onward.

Historical FAQ entries remain evidence for older rules states. They should be
tagged as superseded when a dated official rule change covers the same scope.

A card-specific ruling outside the changed generic scope still requires its own
applicability analysis.
