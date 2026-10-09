# 2026 Expanded ban-overlay audit across official locales

## Research question

Is the repository's dated ban-overlay surface contradicted by any
subsequent announced Expanded ban changes through October 9, 2026?

## Official chronology

- **October 10, 2025:** the Mega Evolution announcement bans Flapple
  with Apple Drop. Four exact prints appear in the repository overlay.
  Official source: https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement
- **April 10, 2026:** the Perfect Order announcement bans Medicham V
  with Yoga Loop in three Evolving Skies prints. The official notice
  dates its announcement March 12 and its effective date April 10.
  Primary source:
  https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-perfect-order-banned-list-and-rule-changes-announcement
- **June 5, 2026:** the Chaos Rising notice (announced May 7)
  explicitly says no Expanded banned-card-list changes.
  Primary source:
  https://www.pokemon.com/us/play-pokemon/about/mega-evolution/mega-evolution-chaos-rising-rule-changes-announcement
- **July 31, 2026:** the Pitch Black notice (announced July 2)
  explicitly says no Expanded banned-card-list changes.
  Its English page could not be directly text-extracted in this audit
  because the web viewer returned an iframe. The **official
  Portuguese-language Pokémon site** does expose its precise
  announcement and effective dates and states:
  "Nenhuma mudança foi feita à lista de cartas banidas para o formato
  Expandido." This means the Expanded banned-card list did not change.
  Primary official source:
  https://www.pokemon.com/br/play-pokemon/sobre/megaevolucao/anuncio-de-mudancas-de-regras-em-megaevolucao-escuridao-absoluta

The English Play! Pokémon Rules & Resources index continues to list
Pitch Black as the latest named rules announcement on October 9,
2026: https://www.pokemon.com/us/play-pokemon/about/card-dex/

## Conclusion

No additional **announced** Expanded bans were identified in the
reviewed 2026 official chronology following Medicham V. The seven
missing-ban print overlays in
tools/build_expanded_legality_baseline.py (four Flapple, three Medicham V)
remain aligned with those announcements.

This finding is narrower than independently certifying every entry
on the full currently effective banned-card list. Historical database
bans and special promotional tournament exclusions remain separately
represented, and a newly issued future announcement would require
another audit.

The dated overlay should therefore retain its seven exact-print entries
and its two original effective dates, rather than claiming new bans
from the Chaos Rising or Pitch Black update names.

## Provenance strength

The Perfect Order, Chaos Rising, and Brazilian Pitch Black texts were
read directly from official Pokémon-hosted search extracts. The
Play! Pokémon rules index independently establishes that Pitch Black
is the most recent linked announcement at audit time. This check
does not rely on Pokémon TCG Live Expanded as a stand-in for paper.
