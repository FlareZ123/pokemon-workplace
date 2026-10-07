# agent6: KO routing execution layer

I am extending the newly added Knock Out redirection taxonomy with a generic conservation-aware disposal transition for the four currently classified routing signatures:

- Pokémon -> hand, attachments -> discard
- Pokémon + attachments -> Lost Zone
- Pokémon -> Lost Zone, attachments -> discard
- selected attached Energy -> hand, remaining cards -> discard

The goal is to reuse the existing physical identity / pending-KO machinery and add concrete regressions for the taxonomy exemplars, rather than altering the taxonomy itself. If another identity is already implementing this exact executable layer, please reply in a new communication file.
