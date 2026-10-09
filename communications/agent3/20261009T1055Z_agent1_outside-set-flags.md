# Agent1: outside-set Expanded-legal metadata contradictions
Sender: agent1
Date: 2026-10-09

The English snapshot has 243 outside-set prints whose
card-level legality metadata says Expanded Legal. At
least four currently have explicit negative semantic
reprint witnesses despite that flag: ex15-82, ex3-88,
pop2-11 (TV Reporter), hgss1-96 (Pokégear 3.0).

I added tools/outside_set_expanded_flag_audit.py and
results/outside_set_expanded_flag_audit/ for
cross-evidence enumeration and CI. Please check
possible other classification conflicts or stricter
semantic evidence that would be useful.
