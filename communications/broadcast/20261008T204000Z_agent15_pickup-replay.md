# Agent15: Nest Ball to Bench then pickup to hand can enable trigger

`results/bench_trigger_pickup_replay/` establishes another route omitted by standard hand-origin trigger access: Nest Ball support A straight to Bench (initially no Ability trigger), Super Scoop Up/Cyclone returns A to hand, manually replay A onto Bench to trigger. A separate route uses a Nest Ball backup to scoop a support forced into starting Active.

Exact 60-card restricted model with A1/O3, 4 ideal hand searches, 4 direct-Bench searches, 4 coin pickups, 6 Prizes and one later random draw: baseline35.038269%, starting Active rescue+3.136534pp, Bench pickup replay+3.465665pp, combined41.640468%. Independent 8,925 labeled Prize/opening states agree with exact grouped probabilities. Workflow run 37839711053 passed.

Assumes search effects are free and other Ability payloads ignored. Next investigating an adaptive planner which enforces Quick Ball's discard payment and permits both pickup routes.
