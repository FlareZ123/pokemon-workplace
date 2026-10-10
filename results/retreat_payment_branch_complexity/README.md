# Exact count of physical Retreat payment branches

## Question

How much larger is the legally enumerable physical payment space than
the inclusion-minimal payment space for Energy cards providing one or
two units each?

## Closed-form result

Let n1 be the number of physical one-unit Energy cards attached,
n2 the number of physical two-unit cards, and c the effective Retreat
Cost. For c > 0, a payment choosing a two-unit and b one-unit cards
is admitted when 1 <= a+b <= c and 2a+b >= c.

The number of different physical payment witnesses is

  FULL = sum C(n2,a) C(n1,b) * I(1 <= a+b <= c <= 2a+b)

where the sum covers 0 <= a <= n2 and 0 <= b <= n1.

The inclusion-minimal subset condition requires that removal of every
chosen card invalidates payment. This is equivalent to

  2a+b - (1 if b > 0 else 2) < c.

Applying the same sum with this additional indicator gives MINIMAL.
For c=0, the empty payment is the only admissible payment.

All counts distinguish individual Energy cards even when their
provided units and printed names are identical. These are counts of
payment subsets for one outgoing Active, before multiplication by
Bench promotions, lock conditions or replacement destination branches.

## Examples

| One-unit | Two-unit | Cost | Full payments | Inclusion-minimal |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 2 | 1 |
| 3 | 2 | 2 | 12 | 5 |
| 4 | 4 | 3 | 78 | 26 |
| 8 | 8 | 4 | 2,352 | 322 |
| 8 | 8 | 6 | 13,678 | 1,428 |

The 16-attached-Energy examples illustrate combinatorial scaling;
they are illustrative states and not estimates of typical tournament
boards. Even a smaller five-card configuration can have 12 legal
payments versus five inclusion-minimal payments.

## Independent verification

`tools/retreat_payment_branch_complexity.py` computes the exact sums
with integer binomial coefficients. The reproduction script separately
constructs distinct EnergyAttachment objects, calls the canonical
`board_object_kernel.legal_retreat_energy_choices`, then tests
inclusion-minimality by physically deleting each selected Energy.

The independent comparison covers 343 parameter combinations:
0 to 6 one-unit cards, 0 to 6 two-unit cards and costs from 0 to 6.
All 343 cases match both counts. The CI workflow also executes
the existing 1,800-scenario physical Retreat-action oracle.

Run `python results/retreat_payment_branch_complexity/reproduce.py`.

## Scope and implications

The existing repository's physical-card-count bound for overpayment
is a conservative implementation based on the Dashing Pouch ruling
establishing that both Double Colorless Energy cards may be paid
for a cost-two Retreat. This result counts exactly that represented
payment rule and does not claim to resolve every imaginable legacy
ruling. Other Energy effects or providers with more than two units
are outside the formula.

The earlier `typed_retreat_payment_pruning` proves a restricted
minimax model can ignore nonminimal payments without changing the
objective. The `retreat_ultraball_payment_bridge` exhibits why
the complete physical action generator must keep those options.
These different algorithmic uses are the motivation for quantifying
the size of the removable branch space.
