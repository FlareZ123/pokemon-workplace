'use strict';

/**
 * Correct one-card randomized opponent-hand effects for source-pinned Twinleaf.
 *
 * Several printed Expanded cards choose a *random* opposing hand card, but
 * their source reducers issue an attacker-owned ChooseCardsPrompt instead.
 * For the ten explicitly audited straight-line reducers below, intercept
 * only that prompt and pass the source reducer a uniformly chosen Card
 * object. Preserve the original discard/reveal/shuffle callbacks verbatim.
 *
 * Exclusions: Dusclops BCR uses a resumable generator, Honchkrow UPR has a
 * reversed empty-hand test, and Wimpod PAR has a coin branch bug. Their
 * reducers require separate source-specific repairs.
 */

const MARKER = Symbol.for('pokemon-workplace.twinleaf.random-one-hand-card-v1');

/**
 * Load exact engine classes from the pinned revision.
 * @param {(name:string)=>any} engine
 * @returns {{CardClass:Function,kind:'attack'|'trainer',attackIndex?:number,label:string}[]}
 */
function buildPinnedSingleCardSpecs(engine) {
  const rows = [
    ['sets/08-sun-and-moon/set-burning-shadows/tormenting-spray','TormentingSpray','trainer',null,'Tormenting Spray BUS125'],
    ['sets/10-scarlet-and-violet/set-paldea-evolved/gothitelle','Gothitelle','attack',0,'Gothitelle PAL92'],
    ['sets/10-scarlet-and-violet/set-prismatic-evolution/tyranitar-ex','Tyranitarex','attack',1,'Tyranitar ex PRE64'],
    ['sets/08-sun-and-moon/set-unbroken-bonds/murkrow','Murkrow','attack',0,'Murkrow UNB108'],
    ['sets/08-sun-and-moon/set-cosmic-eclipse/sandygast','Sandygast','attack',0,'Sandygast CEC126'],
    ['sets/08-sun-and-moon/set-sun-and-moon/zubat','Zubat','attack',0,'Zubat SUM54'],
    ['sets/08-sun-and-moon/set-celestial-storm/lotad','Lotad','attack',0,'Lotad CES36'],
    ['sets/08-sun-and-moon/set-crimson-invasion/pumpkaboo','Pumpkaboo','attack',0,'Pumpkaboo CIN44'],
    ['sets/10-scarlet-and-violet/set-obsidian-flames/togepi','Togepi','attack',0,'Togepi OBF83'],
    ['sets/set-shining-legends/jynx','Jynx','attack',0,'Jynx SLG38']
  ];
  return rows.map(([source, exported, kind, index, label]) => ({
    CardClass: engine(source)[exported],
    kind,
    ...(kind === 'attack' ? { attackIndex: index } : {}),
    label
  }));
}

/**
 * Install source-scoped random-choice hooks idempotently.
 *
 * @param {{
 *  specs: {CardClass:Function,kind:'attack'|'trainer',attackIndex?:number,label:string}[],
 *  AttackEffect:Function,
 *  TrainerEffect:Function,
 *  ChooseCardsPrompt:Function,
 *  random?:()=>number
 * }} adapters
 * @returns {string[]} Every protected exact print, in stable order.
 */
function installPinnedSingleCardRandomHooks(adapters) {
  const {specs,AttackEffect,TrainerEffect,ChooseCardsPrompt} = adapters;
  // Use the game RNG at actual attack resolution, after runOne seeds it.
  const random = adapters.random ?? (() => Math.random());
  const protectedPrints = [];
  for (const spec of specs) {
    const prototype = spec.CardClass.prototype;
    const original = prototype.reduceEffect;
    if (original[MARKER]) {
      protectedPrints.push(spec.label);
      continue;
    }

    /** @this {any} @param {any} store @param {any} state @param {any} effect */
    function randomSingleReduceEffect(store, state, effect) {
      const matches = spec.kind === 'trainer'
        ? effect instanceof TrainerEffect && effect.trainerCard === this
        : effect instanceof AttackEffect &&
          effect.attack === this.attacks[spec.attackIndex];

      if (!matches) return original.call(this,store,state,effect);

      const actor = effect.player;
      const opponent = state.players.find(player => player.id !== actor.id);
      if (opponent.hand.cards.length === 0)
        return original.call(this,store,state,effect);

      const opposingHand = opponent.hand;
      const originalPrompt = store.prompt;
      const hadOwnPrompt = Object.prototype.hasOwnProperty.call(store,'prompt');
      let randomSelections = 0;
      store.prompt = function interceptRandomHandChoice(nextState,prompt,resolve) {
        if (randomSelections === 0 && prompt instanceof ChooseCardsPrompt &&
            prompt.playerId === actor.id && prompt.cards === opposingHand &&
            prompt.options.isSecret === true &&
            prompt.options.min === 1 && prompt.options.max === 1) {
          randomSelections++;
          const draw = random();
          if (!Number.isFinite(draw) || draw < 0 || draw >= 1)
            throw new RangeError('Card-selection RNG must be in [0,1)');
          const chosen = opposingHand.cards[Math.floor(draw * opposingHand.cards.length)];
          return resolve([chosen]);
        }
        return originalPrompt.call(store,nextState,prompt,resolve);
      };

      try {
        const result = original.call(this,store,state,effect);
        if (randomSelections !== 1)
          throw new Error('Pinned ' + spec.label +
            ' reducer no longer exposes its expected single random-hand prompt');
        return result;
      } finally {
        if (hadOwnPrompt) {
          store.prompt = originalPrompt;
        } else {
          delete store.prompt;
        }
      }
    }

    /** @returns {void} */
    function uninstall() {
      if (prototype.reduceEffect === randomSingleReduceEffect)
        prototype.reduceEffect = original;
    }

    Object.defineProperty(randomSingleReduceEffect,MARKER,{value:uninstall});
    prototype.reduceEffect = randomSingleReduceEffect;
    protectedPrints.push(spec.label);
  }
  return protectedPrints;
}

module.exports = {
  MARKER,
  buildPinnedSingleCardSpecs,
  installPinnedSingleCardRandomHooks
};
