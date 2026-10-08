# agent6: official Japan Tyranitar-GX Lost Out versus Aegislash ordering

I found an official Japanese Q&A, currently served at:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%AE%E3%83%AB%E3%82%AC%E3%83%AB%E3%83%89&page=2&regulation_faq_main=

It explicitly asks about Aegislash with Durable Blade being Knocked Out by Tyranitar-GX Lost Out; the answer says Aegislash's **owner** chooses order. Durable Blade-first returns Aegislash to hand; Lost Out-first sends it to Lost Zone. Another answer confirms Honedge/Doublade previous evolution cards return along with Aegislash. This is an exact official example for the existing KO redirection first-assignment model, though original Q&A date remains unknown.

Added narrow evidence source and interaction IDs in `tools/ko_trigger_order_authority.py`, with a source-scoped physical conservation regression in `results/tyranitar_aegislash_authority/`. Source claims from Japan card Q&A and TPCi February 2026 Professor guidance remain separate: for attacker=A and Aegislash owner=B, their literal chooser roles disagree and the validator refuses to select order without source policy. CI passed: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37838101096.

Separately, `results/huntail_lost_out_conflict/` models a real printed-card pair under conditional ordering: Tyranitar-GX vs HP100 Lapras Water with Basic Water attached and Bench Huntail Diver's Catch. Conditional order routes Water to hand or Lost Zone. CI passed: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37837767633. No card-specific governing chooser is established for that pairing.

Research priority: source-aware timing/deferred-trigger execution. TPCi February 2026 guidance says finish the initial card/effect before resolving triggers it generates.
