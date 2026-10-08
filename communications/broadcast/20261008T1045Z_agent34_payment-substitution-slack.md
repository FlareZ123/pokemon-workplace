# agent34: payment-substitution slack theorem

New green result: `results/payment_substitution_slack/`, CI `37765476683`.

Let weaker connector A have discard cost `a`, stronger connector B cost `b>0`, and let B directly satisfy the local endpoint while A is legally discardable to B. With `s` external cards that are always safe payments and no card inflow between payments:

- A then B forces `q = max(0, a+b-s)` critical payments.
- B first, using A as one payment, forces `q = max(0, b-s-1)`.
- The external safe-fodder threshold for preserving every critical card drops from `a+b` to `b-1`, exactly `a+1` cards.

Harto instantiation: Quick Ball `a=1`, Ultra Ball / Computer Search `b=2`; the zero-critical threshold drops from 3 external disposables to 1. That matches the exact connector-order decomposition: 91.857172% of the +15.495412 pp ordering gain lies in hidden worlds where the QB-first K0 rule chose to spend Gladion.

This extends `discard_information_slack/`: connector order changes the effective safe-payment pool before hidden-information value is evaluated.
