# Two Dragapult ex in Regidrago VSTAR: live engine mapping and policy limitation

## Source and scope

The exact-print experimental 60-card [Regidrago / two Dragapult ex candidate](../../decks/regidrago_dragapult_2/) adds a second Dragapult ex (`sv6-130`) and removes one Battle VIP Pass (`swsh8-225`) from the published 2026 Aichi tenth-place [Regidrago baseline](../../decks/regidrago-vstar/). No other card, Energy, ACE SPEC, or printed identity changes. It is a research proposal and was not the published tournament list.

[`simulation/twinleaf/candidate-deck-loader.cjs`](../../../simulation/twinleaf/candidate-deck-loader.cjs) starts with the exact 60 implemented and independently audited printed card names of the published list. It copies the proven already-mapped Dragapult ex full name to replace one proven Battle VIP Pass full name. Its [pinned-engine SFT](../../../simulation/twinleaf/test-candidate-deck-loader.cjs) checks both 60-card multisets, precisely one replacement, source count 1→2 for Dragapult and 3→2 for VIP, source preservation, and all other card quantities unchanged. The [manual CI run 38296229599](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38296229599) passed the candidate mapping SFT and the complete bounded live Store games.

Twinleaf engine pin: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`; native `SimpleTacticsAi`; research uniform shuffle and separate policy/live RNG lanes; identical seed `20261012` with both seats swapped; 350-action and 25-second per-game caps. Deck digests:

- Published Regidrago: `2ad6d7d9bf536a16e1f2d237e344c90b919337296482dd4130f4560feaaf7ab0`.
- Two-Dragapult variant: `3c516f26d43653f5bee5ca708d12627408bae309e1786f666402a43a6e753119`.
- Shared Shadow Rider opponent: `ec02fd642b9293793a17e6865d2554e43b9939c05fdd259d41e823f9a0873555`.

## Same-opponent comparison

| Regidrago build | Seat 1 | Seat 2 | Winner | Turn | Regidrago named attacks |
| --- | --- | --- | --- | ---: | --- |
| Published, [run 38293750862](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293750862) | Shadow Rider | Regidrago | Shadow Rider | 20 | Celestial Roar ×2; Itchy Pollen ×1 |
| Published, same run | Regidrago | Shadow Rider | Shadow Rider | 37 | Celestial Roar ×1; Apex Dragon ×1 |
| Two Dragapult, [run 38296229599](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38296229599) | Shadow Rider | Regidrago variant | Shadow Rider | 20 | Celestial Roar ×2; Itchy Pollen ×1 |
| Two Dragapult, same run | Regidrago variant | Shadow Rider | Shadow Rider | 41 | Celestial Roar ×1 |

All four games completed with no observed engine error or censor. Both Regidrago versions lost twice against Shadow Rider under the weak native playing policy, and neither took a Prize card in these games. The variant bot evolved **two** Regidrago VSTAR and used Legacy Star in its seat-1 game, but never used Apex Dragon in either seat. The first Regidrago seat-2 game contained no VSTAR evolution in the action trace. We have not yet established how often either version placed Dragapult ex in the discard, or exercised Phantom Dive through Apex Dragon.

These matches demonstrate **that the experimental 60-card variant is runnable with existing pinned engine card classes**. They cannot meaningfully test the card's claimed improvement, which depends on a specific early deck-to-discard Item line followed by VSTAR evolution, Energy readiness and copying Dragapult's attacks. The native bot's limited attack setup, Bench priorities and discard choices dominate the observed games.

## Relation to stronger source-level evidence

The exact [joint first-turn Regidrago V + discarded Dragapult access analysis](../../regidrago_joint_launch/), the [K0-aware window](../../regidrago_k0_joint_launch/), and the [four-channel source requirement](../../decks/regidrago_dragapult_2/vstar_natural.md) support improved source availability for the candidate under precisely stated restricted action and Energy assumptions. Those are distinct from full-game strength. The reproducible headless match confirms compatibility while exposing why a *strategy-aware Regidrago bot* remains essential before estimating competitive win-rate change.

Research classification: verified source-print mapping, live headless executable traces, negative evidence for native-bot ability to test the desired attack line. No claim of superior competitive deck.
