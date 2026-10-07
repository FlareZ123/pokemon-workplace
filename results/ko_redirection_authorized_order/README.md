# Source-authorized Knock Out redirection

This result connects source-scoped effect-order authority to the existing physical Knock Out route executor.

The bridge is `tools/ko_redirection_authorized_order.py`; the regression is `results/ko_redirection_authorized_order/reproduce.py`.

It reuses `ko_trigger_order_authority.py` for source claims and `knockout_redirection_ordering.py` for physical destination resolution. Current repository evidence records a source conflict for Lost City plus Reuniclus: February 2026 TPCi Professor guidance assigns during-turn Knock Out trigger ordering to the current player, while current Japan and Asia card-specific Q&A assign this interaction to the Knocked Out Reuniclus's owner.

The bridge instantiates each selected source claim to a concrete player ID. It refuses execution when no claim applies, required player context is missing, selected claims name different players, the submitted order came from another player, or the effect order is invalid.

A source-level disagreement can still collapse safely in a concrete state. If the current player and the Knocked Out Pokemon's owner are the same player, both source families name the same chooser, so the physical order can execute without assuming which abstract rule has precedence.

The regression reuses the existing three-card evolution-stack witness. An authorized Lost City-first order sends the full Pokemon stack to the Lost Zone. An authorized return-effect-first order sends the full stack to hand. Attachments follow their explicit discard routes and card totals remain conserved.

The safe chain is:

`selected sources -> concrete chooser -> authorized effect order -> physical destinations -> conserved state transition`

The bridge does not select a regional or tournament rules source. That policy remains explicit caller input. Trigger eligibility and non-destination effect semantics also remain upstream.
