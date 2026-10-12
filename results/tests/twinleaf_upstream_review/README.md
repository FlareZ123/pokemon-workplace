# Reviewable upstream Twinleaf monitoring

Agent 23, 12 October 2026.

## Motivation

The research uses a Gitlink to the upstream Twinleaf codebase and a strict engine revision in research adapters. Silent upstream changes can invalidate behavior, card coverage or saved experiment results. The existing submodule is at vendor/twinleafgg; upstream is https://github.com/twinleafgg/twinleafgg.git, branch main.

The new GitHub Actions workflow at .github/workflows/twinleaf-upstream-review.yml checks for new upstream commits **weekly on Monday at 05:37 UTC** and also offers manual workflow_dispatch. It does not schedule expensive compilation every time someone commits to the main research branch.

## Review procedure

1. Read the exact committed Gitlink SHA from the local research checkout.
2. Read the upstream main Git SHA, without writing to the upstream project.
3. If unchanged, exit after the lightweight discovery job. As checked on 12 October 2026, both were 3348ebdc898f175a2ed8f999133cd13d1afd01f5.
4. If changed, initialize only vendor/twinleafgg and fetch the newer commit. Recursive checkout is deliberately avoided because the pinned upstream has a broken nested vendor/pokemon-cards-css entry.
5. Use the proposed engine's .nvmrc and npm lockfile, compile TypeScript, then run the selected print coverage, deck loading, Ability-hook, RNG, and score-accounting regressions.
6. Only after the checks pass, push a branch named automation/twinleaf-<12-character-commit-prefix> and open a **draft** pull request. The default-branch Gitlink remains pinned.
7. Require human/agent review of card-effect parity, engine hooks and hardcoded revision constants before merging. The draft PR explicitly says that compilation and static tests cannot prove full paper Expanded correctness.

The proposal uses GitHub Actions' built-in token for branch creation and PR submission. If repository settings prohibit automated PR creation, the action will fail explicitly rather than silently update the default branch. Existing branches and open PRs for the same candidate are reused, avoiding duplicate proposals on repeated scheduled runs.

## Validation status

The workflow definition and Gitlink SHA comparison were inspected in the live repository. The checked upstream main SHA is identical to the pinned Gitlink as of 12 October 2026, so the update path has not been exercised. Full Windows-runner compilation and automated PR creation remain untested. Treat this as a safely guarded first implementation requiring a manual end-to-end dry run when upstream changes.

The trial currently validates selected research components and does not run full competitive matches. It deliberately does not auto-update hard-coded pinned SHA constants within experiment programs. Changes to those constants require separate review and reproducibility checks.

## Follow-up

The next useful check is a controlled dry run on a non-default branch using an intentionally different upstream revision, with the proposal gated against accidental paper legality changes. Record any failed dependency, node-version, hook or CI permissions check before enabling merge eligibility. Keep the resulting proposed code revision distinct from the validated current pin.
