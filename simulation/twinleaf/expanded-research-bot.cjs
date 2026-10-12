'use strict';

const { SimpleBot } = require('../../vendor/twinleafgg/ptcg-server/output/simple-bot/simple-bot');
const { Format } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/card/card-types');

/**
 * Research-owned Twinleaf bot that uses an explicitly supplied deck.
 *
 * Twinleaf SimpleBot.loadDeck() loads a random database deck and does not read
 * BotClient.setDeck(). Override only that deck-selection boundary, preserving
 * the pinned engine's existing SimpleGameHandler and action policy.
 */
class ExpandedResearchBot extends SimpleBot {
  /**
   * @param {string} name
   * @param {string[]} deck 60 Twinleaf fullName identifiers, not TCGdex print IDs.
   * @param {object} [options] Existing SimpleBot options.
   */
  constructor(name, deck, options = {}) {
    if (!Array.isArray(deck) || deck.length !== 60 ||
        deck.some(card => typeof card !== 'string' || card.trim() === '')) {
      throw new TypeError('A Twinleaf Expanded deck must contain exactly 60 non-empty fullName strings');
    }
    super(name, options, [Format.EXPANDED]);
    this.setDeck(Format.EXPANDED, [...deck]);
  }

  /** @returns {Promise<string[]>} An independent copy of the configured deck. */
  async loadDeck() {
    const deck = await this.getDeck(Format.EXPANDED);
    return [...deck];
  }
}

module.exports = { ExpandedResearchBot };
