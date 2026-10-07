# Escape Board Retreat exception

## Question

Can an Asleep or Paralyzed Active Pokemon use the ordinary Retreat action when
Escape Board is attached and its Tool effect is active?

## Finding

Yes.

Escape Board `sm5-122` is effectively legal in paper Expanded and says that
the attached Pokemon's Retreat Cost is one Colorless less and that it can
retreat even if Asleep or Paralyzed.

Both shared Retreat kernels previously rejected Asleep or Paralyzed before any
Tool-specific exception could be considered. That made an explicitly legal
Escape Board line unreachable.

The fix is narrow:

- a live Escape Board Tool bypasses the Asleep/Paralyzed Retreat prohibition;
- a temporary explicit "can't retreat" effect still blocks the action;
- if the Tool effect is disabled, Escape Board no longer bypasses the Special
  Condition prohibition;
- Retreat Cost remains a separate input to the payment layer, so the Tool's
  one-unit reduction is handled by Retreat Cost semantics rather than by the
  permission exception.

## Regression

`results/escape_board_retreat_exception/reproduce.py` checks both current
Retreat kernels:

- active Escape Board permits ordinary Retreat while Asleep;
- active Escape Board permits ordinary Retreat while Paralyzed;
- Tool-effect-disabled Escape Board does not permit the Asleep retreat;
- the board-object kernel still rejects an explicit temporary retreat lock even
  when Escape Board is active;
- the exact bundled Escape Board card text and effective legality are verified.

## Architectural implication

"Can this Pokemon retreat?" is not equivalent to checking only its Special
Condition. Retreat permission can contain card-specific exceptions layered over
the base rule.

The resulting action gate is ordered:

1. explicit effects that say the Pokemon cannot retreat remain prohibitions;
2. Asleep/Paralyzed normally prohibit retreat;
3. an applicable Escape Board effect overrides only that Special Condition
   prohibition;
4. the independently derived effective Retreat Cost determines payment.

This keeps permission semantics separate from cost semantics while allowing
both to compose in the final Retreat transaction.
