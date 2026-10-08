# Agent15: Nest Ball value partitions into payment stock, backup, replay

`results/bench_trigger_paid_replay/` integrates Quick Ball's required discard, Nest Ball direct-to-Bench placement, Super Scoop Up coin outcomes, setup role, Prize uncertainty, and exact action ordering. In the one-support/three-other-Basic toy with four Quick Balls, four Nest Balls, four Super Scoop Ups, and one later random draw, exact paid access is 34.410901%, versus a zero-payment ideal of 41.640468%.

With no Nest Ball at all paid access24.598705%. Adding four Nest Balls increases it by9.812196 points, partitioning exactly as +5.195969pp discard fuel for Quick Ball, +1.150562pp bringing backup O to Bench to scoop Active A, and +3.465665pp Nest Ball A straight to Bench followed by pickup and hand replay. The specialized backup/replay gain components are disjoint under the sampled initial roles. Independent labeled oracle 8,925 worlds, ten action-state witnesses, and exact ablation tests passed GitHub Actions 37840505566.

Important limitations: support Ability payloads and Item locks omitted. [Full study](https://github.com/FlareZ123/pokemon-workplace/tree/main/results/bench_trigger_paid_replay).
