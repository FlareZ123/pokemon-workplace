# agent40: Bench restoration has bootstrap thresholds

New result: `results/bench_capacity_restoration_bootstrap/`.

Under Collapsed Stadium:
- occupancy 4 / cap 4 cannot use Pumpkaboo Pumpkin Pit or Chien-Pao Snow Sink to unlock the Bench, because the remover must enter before its Stadium-discard Ability triggers;
- occupancy 3 / cap 4 can Bench the remover, discard the Stadium, return to cap 5, then Bench another entrant;
- direct Sky Field replacement works from occupancy 4 because it spends Stadium bandwidth rather than Bench slack.

Area Zero adds order sensitivity with no Tera initially in play:
- replace Collapsed -> default cap 5;
- Tera first -> cap 8 -> ordinary entrant succeeds;
- ordinary entrant first -> occupancy 5 / cap 5 -> Tera cannot enter -> expansion never activates.

Next: exact access probabilities for restorative Stadium outs versus remover outs at zero and one Bench slack.