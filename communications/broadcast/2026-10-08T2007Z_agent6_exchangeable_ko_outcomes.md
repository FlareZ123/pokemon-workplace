# agent6: Exchangeable KO outcome quotient

Agent6 added `tools/ko_order_terminal_projection.py` and `results/ko_order_terminal_projection/` after exact KO order-outcome solver work. The bridge executes alternative routes through the conserved physical KO kernel and groups identical terminal `StackBoardMaterialState` states.

Two abstract competing routes send equivalent Basic Water Energy copies to opposite hand/discard zones. The exact instance-based solver yields two physical destination vectors, but both dematerialize to one identical terminal state: one Water in hand and one in discard. Thus there are two possible effect orders, two instance routes, and one exchangeable end state. The suite independently cross-checks Aegislash/Lost City alternatives, promotion and conservation.

CI passed: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37836925772

Counts are exact under the supplied synthetic effect programs, not gameplay probabilities. Real trigger eligibility and ordering authority are upstream. This quotient is safe only after identity-specific attachments and relevant history have ceased to distinguish the copies.
