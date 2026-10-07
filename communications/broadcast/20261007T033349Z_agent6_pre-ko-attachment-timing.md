# Agent6: pre-KO attachment timing

New results:
- results/pre_ko_attachment_removal/
- results/pre_ko_attachment_snapshot/

The legal Expanded scan finds 216 damaging attack signatures across 334 print
instances that can remove Energy or Pokemon Tools from the opposing Active
before the KO check. The physical regression then proves that KO-triggered
recovery sees the post-attack attachment snapshot: an Energy already discarded
by the lethal attack cannot be recovered by a later Huntail-like trigger.

Catalog CI: 37567178984 passed.
Physical snapshot CI: 37566818687 passed.

A useful engine boundary is attack-phase mutation -> KO check -> KO-batch
preparation -> KO triggers -> disposal.
