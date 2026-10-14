'use strict';
const assert = require('node:assert/strict');
const {atLeastOne} = require('./blind-topdeck-trainer-tactic.cjs');

/**
 * Observation-consistent K0 estimator for four exact printed implementations of three full-deck paid-search
 * Items in the pinned Twinleaf engine. The combined hidden deck-plus-Prize
 * multiset is reconstructed as an exchangeable pre-first-search pool.
 * K1 deck inspections, positioned Prize knowledge and deliberate deck-order
 * manipulation are outside this provisional model.
 *
 * For other Items the inherited native evaluator is intentionally retained.
 * Thus this class is an experimental intervention, not a fully blind bot.
 *
 * @param {Function} NativeTactic Pinned PlayTrainerTactic constructor
 * @param {{
 *   TrainerCard:Function,TrainerType:object, PokemonCard:Function,Stage:object,
 *   CardType:object,pokemonHasCardType:Function,PlayCardAction:Function,
 *   PlayerType:object,SlotType:object,StateScore:Function
 * }} engine Pinned runtime card and tactic contracts
 * @returns {Function} A tactic constructor accepted by SimpleTacticsAi
 */
function makeBlindPaidSearchTactic(NativeTactic, engine) {
  const {TrainerCard, TrainerType, PokemonCard, Stage, CardType,
    pokemonHasCardType, PlayCardAction, PlayerType, SlotType, StateScore} = engine;
  for (const ctor of [NativeTactic, TrainerCard, PokemonCard,
    pokemonHasCardType, PlayCardAction, StateScore]) {
    assert.equal(typeof ctor, 'function');
  }
  const isPokemon = card => card instanceof PokemonCard;
  const isBasic = card => isPokemon(card) && card.stage === Stage.BASIC;
  const isTreasure = card => isPokemon(card) &&
    (pokemonHasCardType(card, CardType.PSYCHIC) ||
      pokemonHasCardType(card, CardType.DRAGON));
  const paidSpecs = Object.freeze({
    'Quick Ball SSH': {payment: 1, eligible: isBasic},
    'Ultra Ball SVI': {payment: 2, eligible: isPokemon},
    'Ultra Ball BRS': {payment: 2, eligible: isPokemon},
    'Mysterious Treasure FLI': {payment: 1, eligible: isTreasure},
  });

  return class BlindPaidSearchTactic extends NativeTactic {
    /**
     * @param {{scores:{hand:{
     *   cardScore:number,hasPokemon:number,hasBasicWhenBenchEmpty:number,itemScore:number
     * }}}} options Pinned bot settings
     */
    constructor(options) {
      super(options);
      this.publicHandScore = new StateScore(options);
    }

    /**
     * Estimate a paid-search action's *incremental* hand value under an
     * exchangeable K0 allocation, using only combined unknown inventory and
     * publicly visible payment candidates.
     *
     * Payments are selected by individually scored marginal discard losses.
     * This first-order heuristic does not claim to solve multi-card synergy
     * or the true value of a hand in competitive play.
     *
     * @param {object} state Native State
     * @param {object} player Native Player
     * @param {object} item Pinned Item instance
     * @param {{payment:number,eligible:Function}} spec Search contract
     * @returns {number} Estimated score delta; -Infinity when unplayable
     */
    estimatedDelta(state, player, item, spec) {
      if (player.deck.cards.length === 0) return -Infinity;
      const otherCards = player.hand.cards.filter(card => card !== item);
      if (otherCards.length < spec.payment) return -Infinity;

      const unseen = [...player.deck.cards,
        ...player.prizes.flatMap(slot => slot.cards)];
      const eligible = unseen.filter(spec.eligible);
      const basicEligible = eligible.filter(isBasic);
      const deckSize = player.deck.cards.length;
      const probability = atLeastOne(unseen.length, eligible.length, deckSize);
      const basicProbability = atLeastOne(unseen.length, basicEligible.length, deckSize);
      const scores = this.options.scores.hand;
      const heldPokemon = player.hand.cards.some(isPokemon);
      const heldBasic = player.hand.cards.some(isBasic);
      const emptyBench = player.bench.every(slot => slot.cards.length === 0);

      const pickupValue =
        probability * (scores.cardScore + (heldPokemon ? 0 : scores.hasPokemon)) +
        (emptyBench && !heldBasic ? basicProbability * scores.hasBasicWhenBenchEmpty : 0);

      const paymentLosses = otherCards.map(card =>
        -this.publicHandScore.getCardScore(state, player.id, card))
        .sort((left, right) => left - right);
      const paymentCost = paymentLosses.slice(0, spec.payment)
        .reduce((total, loss) => total + loss, 0);
      return pickupValue - scores.itemScore - paymentCost;
    }

    /**
     * @param {object} state Native authoritative state
     * @param {{id:number,hand:{cards:object[]},deck:{cards:object[]},prizes:object[]}} player
     * @returns {object|undefined} Item action if estimated delta is positive
     */
    useTactic(state, player) {
      const items = player.hand.cards.filter(card =>
        card instanceof TrainerCard && card.trainerType === TrainerType.ITEM);
      if (items.length === 0) return undefined;

      const baseline = this.getStateScore(state, player.id);
      const target = {player: PlayerType.ANY, slot: SlotType.BOARD, index: 0};
      let bestGain = 0;
      let bestAction;
      for (const item of items) {
        const index = player.hand.cards.indexOf(item);
        const action = new PlayCardAction(player.id, index, target);
        const spec = paidSpecs[item.fullName];
        const delta = spec
          ? this.estimatedDelta(state, player, item, spec)
          : (() => {
              const score = this.evaluateAction(state, player.id, action);
              return score === undefined ? -Infinity : score - baseline;
            })();
        if (delta > bestGain) {
          bestGain = delta;
          bestAction = action;
        }
      }
      return bestAction;
    }
  };
}

module.exports = {makeBlindPaidSearchTactic};
