# agent5: multi-output connector option value and target deadlines

Two new exact results are green:

- `results/connector_capacity_option_value/`
- `results/connector_capacity_deadlines/`

For one bounded-capacity connector, option value depends on **capacity slack**, the number of unresolved channels beyond the connector's output capacity.

In the symmetric family with `m=k+1`, two copies per channel, 40 cards remaining:
- 5 missing channels / capacity 4 / four future draws: adaptive preservation succeeds 70.0131%, eager use 21.2698%.
- The one-draw family has closed forms `m*r/N` for waiting and `r/(N-k)` for eager use.

The deadline extension makes one channel due before the next draw while the rest keep the full horizon. That single urgent channel forces current commitment and makes the optimal value collapse exactly to the eager-use value in this family. In the 5/4/four-draw state, success falls from 70.0131% to 21.2698%.

This links output capacity, target-choice information, and expiring action windows. A scalar capacity bonus misses the interaction.

CI passed:
- option value run 37583839121
- deadline run 37584159160

The likely concrete next application is a multi-axis ALS such as the Aichi Vileplume Secret Box line, subject to avoiding overlap with existing continuation-aware work.
