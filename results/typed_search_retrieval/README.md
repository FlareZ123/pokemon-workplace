# Typed search retrieval before demand projection

## Question

Should a typed search action be generated from strategic demand first, or should the physical retrieval choice exist before demand evaluation?

The physical retrieval should exist first.

Implementation: `tools/typed_search_retrieval.py`  
Regression: `results/typed_search_retrieval/reproduce.py`

## Counterexample

Guzma & Hala has a Stadium search axis. After its optional two-card discard, it also has a Pokemon Tool axis and a Special Energy axis.

Consider one valid target for each axis while the immediate strategic demand is only one Special Energy.

The earlier demand-first allocator emits the DCE-only choice because Stadium and Tool cannot be assigned to the declared Special Energy demand.

The raw retrieval layer instead enumerates all eight legal restricted-search subsets. Retrieving only the Special Energy and retrieving Stadium, Tool, and Special Energy both satisfy the same immediate demand, while producing different future hand states.

## Separation

`enumerate_typed_retrieval_actions()` models card-text retrieval capacity and target depletion without requiring every selected card to satisfy a declared demand.

`project_retrieval_to_demands()` evaluates what strategic demand can be satisfied by an already-defined retrieval. Retrieved cards may remain strategically unassigned.

This preserves optional side payloads for later policy evaluation.

## Real-list relevance

`results/iron_thorns_gnh_side_payload/` independently finds that, conditional on the modeled Aichi Iron Thorns T1 line already paying Guzma & Hala's two-card optional discard to obtain Double Colorless Energy, a Pokemon Tool remains searchable in more than 99% of those states across all three published lists.

## Interpretation

Optional search output is a decision variable. Taking every available side payload is not assumed optimal. The representation keeps minimal and fuller retrieval choices separate so later policy evaluation can compare their continuation value.

## Limits

This result does not yet execute the raw retrieval into zone state or integrate it into the atomic Trainer transaction. The next step is to let those execution layers consume a raw retrieval witness while demand remains a separate projection.
