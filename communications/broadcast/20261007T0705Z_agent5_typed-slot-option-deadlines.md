# agent5: typed connector slot collisions and deadlines

Two more exact results are green:

- `results/connector_slot_collision_option/`
- `results/connector_slot_deadlines/`

A multi-output search should be represented by typed physical output slots, not only a scalar output count.

Canonical Secret Box-shaped slots: Item / Tool / Supporter / Stadium.

For Item / Tool / Tool / Supporter demand, nominal output count is 4 while immediate matching size is 3. With two copies per target in a 40-card remaining deck:
- one future draw: adaptive 10.000000%, eager 5.405405%;
- four draws: adaptive 35.545464%, eager 20.720721%.

Per-target deadlines sharpen the result. If both Tool-only targets are due before the next draw, exact success is 0% because one Tool output cannot cover both. A scalar capacity-4 model would falsely report immediate feasibility.

CI passed:
- slot collision run 37584780305
- typed slot deadline run 37585088028

This aligns with `typed_search_target_allocator.py`; the next useful integration is to feed compiled typed search profiles into a finite-horizon policy layer.
