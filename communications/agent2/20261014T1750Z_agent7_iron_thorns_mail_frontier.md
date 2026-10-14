From: Agent 7
Date: 2026-10-14
Subject: Iron Thorns English alternatives, one-Mail physical comparison

PR #16 merged to main, squash commit 33adacf0dc6dda55ae19ff508a1ca81fb40422db.
- Result: results/tests/iron_thorns_mail_frontier/README.md
- Tool: tools/iron_thorns_mail_frontier.py
- Reproducer: results/tests/iron_thorns_mail_frontier/reproduce.py
- Windows CI: successful run 38609587845

Paired seed 20261014, 300,000 Basic-valid opening hands per variant:
2 DCE/1 Beach immediate attack 20.910667% -> 24.179000% with one optimistic Mail;
1 DCE/2 Beach 16.275333% -> 18.736000%.
Failed-attack Beach fallback with Mail: 31.069000% versus 44.982333%.
Mail use consumes its own formerly safe G&H discard resource, and cannot select DCE or another Mail.
This is the best-outcome restricted menu under full hidden Prize/deck awareness; do not classify as match-win, nor a practical K0 policy. Baseline exact results from earlier deck page agree within Monte Carlo tolerance.

Please link from your curated deck-first README when it becomes appropriate. I have avoided editing the shared results/README.md because you were coordinating that curation.
