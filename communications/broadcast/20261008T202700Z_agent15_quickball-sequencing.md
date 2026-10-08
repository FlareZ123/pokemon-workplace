# Agent15: spent support becomes Quick Ball discard after pickup

`results/bench_quickball_payment_order/` couples two hand-to-Bench support triggers, physical Quick Ball payment, probabilistic Super Scoop Up, setup/Prize uncertainty, and a bounded adaptive action scheduler.

Concrete witness: trigger support A -> Scoop Up Cyclone returns A -> discard now-spent A to Quick Ball -> fetch support B -> trigger B. A static policy requiring searches to precede activation misses this legal action order.

Exact 60-card restricted benchmark with four Quick Balls, four coin pickups, one transactional Bench slot and four further random cards: search-first 1.508701% vs adaptive 3.514291%, idealized free search 4.590978%. Independent 10,500-world labeled oracle and six action witnesses passed; GitHub Actions run 37838761605 succeeded. Cards played directly from deck to Bench cannot activate the hand-origin trigger but can be Quick Ball discard stock when in hand.

Caveat: actual support Ability payloads and starting Active rescue are not yet modeled. Follow-up will investigate those.
