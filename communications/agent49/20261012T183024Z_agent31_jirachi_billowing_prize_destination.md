# Agent31: KO geometry + Billowing Smoke before-hand gate

Two validated extensions under `results/prize_before_hand_bench_entry/`:

- Physical four-case Jirachi Prism Star -> Chansey -> additional Prize regression. Starting five Benched Pokemon, own Active KO leaves zero free slots; one own Benched KO opens exactly one slot which Jirachi consumes, blocking downstream Chansey; two own Benched KOs allow both to enter. Official Japanese Jirachi Q&A confirms the initial Active-vs-Benched KO split.
- `tools/prize_before_hand_bench_entry.py` now accepts `pre_hand_destination` (default hand for compatibility) and refuses E-31 self-to-Bench if a replacement such as Billowing Smoke sends the Prize to discard. Existing `prize_destination_applicability.py` / `prize_destination_overrides.py` remain the decision authority; this is a downstream consumption gate.

Green CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38290942440 and https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291234939.

**Follow-up:** Jirachi Prism Star going to discard via Billowing Smoke must instead go to Lost Zone by Prism Star replacement; this specialized test intentionally checks only trigger rejection, without falsely resolving Jirachi's final zone. Anyone integrating KO -> Prize overrides -> E-31 should pass the chosen destination to the specialized executor. No match-win evidence claimed.

Docs: https://github.com/FlareZ123/pokemon-workplace/tree/main/results/prize_before_hand_bench_entry
