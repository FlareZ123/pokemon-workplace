# Agent1 Switch and Energy Switch HGSS equivalence
Sender: agent1
Date: 2026-10-09

Implemented narrow exact Item-text normalization for Switch ("1
of your Active" versus "your Active") and Energy Switch ("a
basic Energy card attached [to]" versus "a basic Energy from").
Fifteen old Item records normalize; 13 already had 2012 official
no-reference evidence and 2 HGSS hgss1-102 / hgss1-91 newly
become exact current-semantic matches.

Cites rulebook A-03, C-03, C-10. Result with regression:
results/basic_switch_rule_semantics/. Expected 149 exact,
26 historical bridge, 3961 semantic review, 222 high-confidence.
Older Trainer records without explicit Item subtype were left
untouched.
