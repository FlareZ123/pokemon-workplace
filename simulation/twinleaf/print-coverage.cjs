'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '../..');

/**
 * @typedef {{name:string, set:string, setNumber:string, fullName:string}} EngineCard
 * @typedef {{qty:number, name:string, printId:string}} PrintedEntry
 */

/**
 * Parse the two published 2026 Aichi baseline decklists, preserving exact
 * print IDs. Fails on changed heading/table structure instead of silently
 * analyzing a partial deck.
 * @param {string} markdown
 * @returns {Record<string, PrintedEntry[]>}
 */
function parseBaselineDecks(markdown) {
  const result = { vileplume: [], shadow_rider: [] };
  let selected = null;
  for (const line of markdown.split(/\r?\n/)) {
    if (line.startsWith('## 2026 Aichi Open League runner-up:')) {
      selected = 'vileplume';
    } else if (line.startsWith('## 2026 Aichi champion:')) {
      selected = 'shadow_rider';
    } else if (line.startsWith('## ')) {
      selected = null;
    }
    if (!selected) continue;
    const match = /^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*([a-zA-Z0-9]+-[a-zA-Z0-9]+)\s*\|$/.exec(line);
    if (match) {
      result[selected].push({ qty: Number(match[1]), name: match[2].trim(), printId: match[3] });
    }
  }
  for (const [name, entries] of Object.entries(result)) {
    if (entries.length < 15 || entries.reduce((sum, entry) => sum + entry.qty, 0) !== 60) {
      throw new Error(`Incomplete ${name} baseline: ${entries.length} entries`);
    }
  }
  return result;
}

/** @param {string} value */
function cleanNumber(value) {
  const text = String(value).trim();
  return /^0*\d+$/.test(text) ? String(Number(text)) : text.toUpperCase();
}

/** @param {string} value */
function cleanName(value) {
  return value.normalize('NFKC').replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim().toLowerCase();
}

/**
 * Return a conservative inventory of exact-print implementations. No
 * alias/substitution can become an exact match without the same set number.
 *
 * @param {PrintedEntry} entry
 * @param {Map<string, string>} paperSetCodes
 * @param {EngineCard[]} cards
 */
function matchPaperPrint(entry, paperSetCodes, cards) {
  const dash = entry.printId.lastIndexOf('-');
  if (dash < 1) throw new Error(`Unrecognized print ID: ${entry.printId}`);
  const sourceSetId = entry.printId.slice(0, dash);
  const sourceNumber = cleanNumber(entry.printId.slice(dash + 1));
  const sourceSetCode = paperSetCodes.get(sourceSetId);
  if (!sourceSetCode) {
    return { ...entry, sourceSetCode: null, status: 'unmapped_set', matches: [] };
  }

  const samePrint = cards.filter(card =>
    String(card.set).toUpperCase() === sourceSetCode.toUpperCase() &&
    cleanNumber(card.setNumber) === sourceNumber);
  const exact = samePrint.filter(card => cleanName(card.name) === cleanName(entry.name));
  const matches = exact.length ? exact : samePrint;
  const status = exact.length === 1 ? 'exact' :
    exact.length > 1 ? 'ambiguous_exact' :
    samePrint.length ? 'name_mismatch_review' : 'missing_print';

  return {
    ...entry, sourceSetCode, status,
    matches: matches.map(card => ({
      fullName: card.fullName, name: card.name, set: card.set, setNumber: card.setNumber
    }))
  };
}

/** @returns {EngineCard[]} Cards from the *pinned* Twinleaf sources. */
function loadImplementedCards() {
  const sets = require('../../vendor/twinleafgg/ptcg-server/output/sets');
  const cards = [];
  for (const [key, value] of Object.entries(sets)) {
    if (!key.startsWith('set') || !Array.isArray(value)) continue;
    for (const card of value) {
      if (card && typeof card.fullName === 'string' && typeof card.setNumber === 'string') {
        cards.push(card);
      }
    }
  }
  return cards;
}

/**
 * @returns {Record<string, ReturnType<typeof matchPaperPrint>[]>}
 */
function auditAichiBaselines() {
  const markdown = fs.readFileSync(path.join(ROOT, 'results/competitive_deck_baselines/README.md'), 'utf8');
  const decks = parseBaselineDecks(markdown);
  const sets = JSON.parse(fs.readFileSync(path.join(ROOT, 'resources/sets/en.json'), 'utf8'));
  const paperSetCodes = new Map(sets.filter(set => set.ptcgoCode).map(set => [set.id, set.ptcgoCode]));
  const implemented = loadImplementedCards();
  return Object.fromEntries(Object.entries(decks).map(([name, entries]) =>
    [name, entries.map(entry => matchPaperPrint(entry, paperSetCodes, implemented))]));
}

module.exports = {
  parseBaselineDecks, cleanNumber, cleanName,
  matchPaperPrint, loadImplementedCards, auditAichiBaselines
};
