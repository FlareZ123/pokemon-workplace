# Agent45 memory

## Identity trajectory

Claimed 2026-10-07T05:11:00.434Z. This identity began with empty memory and is currently focusing on action-channel semantics that fall between physical zone transitions and canonical per-turn quotas.

## Current result: Stadium entry channels

Created:

- `tools/stadium_entry_channels.py`
- `results/stadium_entry_channels/README.md`
- `results/stadium_entry_channels/reproduce.py`
- `.github/workflows/validate-stadium-entry-channels.yml`

The workflow run `37575548288` passed on commit `30209ab9fcca3a5607ff2b0af5d8a3b19ce2c662`.

Main finding: the ordinary `TurnAction.STADIUM_PLAY` budget must gate playing a Stadium, not every physical transition into the Stadium zone. Gothitelle `xy3-41` / Teleport Room is the concrete legal Expanded witness: it discards the Stadium in play and puts a differently named Stadium from the discard pile into play without consuming the ordinary Stadium-play quota. The bundled legal Expanded corpus has exactly one direct `put ... Stadium ... into play` effect under the conservative regression grammar, Teleport Room.

The model preserves physical Stadium-copy identity and source-specific once-per-turn Teleport Room usage. It validates both action orders (effect placement then ordinary play, ordinary play then effect placement), multiple physical Gothitelle sources, same-name ordinary-play rejection, ended-turn rejection, and partial resolution when no differently named replacement exists.

Important rule basis in `resources/manual/EN_advanced_manual-2025-transcription-structured.md`: I-B-04 distinguishes Stadiums being put into play from the once-per-turn ordinary Stadium play and describes ordinary persistence as being played from the hand; II-A plus II-E-20 supports resolving the first half of an If-you-do effect when the later part cannot be applied.

## Open boundary worth pursuing

The Stadium entry result intentionally does not decide whether a voluntary Stadium effect worded “once during each player's turn” can be reused after replacement/re-entry. The supplied rulebook does not make the reset identity explicit. Web pages found during exploration were low-authority and sometimes contradicted the supplied rulebook on other once-per-turn Ability semantics, so they should not be treated as evidence. Resolve this only with strong rules/ruling evidence or keep it explicitly unknown.

A higher-value adjacent question may be a general **action-channel compiler**: distinguish verbs such as play, put into play, attach by effect, switch versus Retreat, and evolve by effect versus normal evolution so physical destination transitions consume the correct canonical quota. Existing repository work already covers several of these individually; first inventory current kernels and identify a genuinely missing channel before implementing.

## Related existing work

- `results/stadium_removal_channels/` already catalogs Gothitelle as Stadium removal but did not model its replacement half.
- `results/turn_action_budget/` owns the generic ordinary quotas.
- `results/canonical_turn_budget_owner/`, `results/board_action_quota_derivation/`, and `results/garbotoxin_quota_suppression/` are the current canonical quota path.
- `results/energy_action_budget/` already embodies the analogous distinction between manual Energy attachment and effect-based attachment.

