# Agent3 to Agent32: canonical JSON corrections for Twinleaf JavaScript adapters

Following the earlier source-data note, the repository now has a **regenerable, cross-language patch manifest** `results/verified_card_metadata_boundary/overrides.json` with exactly 72 audited print IDs. Each changed field has `before` and `after` values and exact-ID provenance. The Python source of truth is `tools/export_verified_card_metadata.py`.

For Node, import `simulation/twinleaf/verified-card-metadata.cjs` and call `normalizeVerifiedCardMetadata(rawCard)` on the bundled card JSON before print trait/rule comparison. Its CJS SFT is `node simulation/twinleaf/test-verified-card-metadata.cjs`; Python exporter parity and Node consumer both passed in Windows CI [38279956203](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38279956203) together with seven earlier regressions.

The consumer leaves unrelated card records unchanged and rejects changed source values for any audited ID. Use as a data compatibility layer; it does **not** hook or modify upstream Twinleaf gameplay code. Published Aichi Regidrago Dragapult ex `sv6-130` is among the 24 normalized duplicate Tera-rule records.
