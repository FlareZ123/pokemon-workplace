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

/**
 * TCGdex promotional collector numbers carry a prefix absent from some
 * Twinleaf engine setNumber values (e.g. XYP XY177 -> XYP 177).
 * Restrict prefix stripping to known promo set codes; normal numbered sets
 * must retain their exact collector-number semantics.
 *
 * @param {string} sourceNumber Printed collector number (part after final '-').
 * @param {string} sourceSetCode Mapped printed set code from resources/sets/en.json.
 * @returns {string} Comparable collector number.
 */
function normalizePromoPrintNumber(sourceNumber, sourceSetCode) {
  const cleaned = cleanNumber(sourceNumber);
  const prefixBySet = { XYP: 'XY', SMP: 'SM', BWP: 'BW', SWSHP: 'SWSH' };
  const prefix = prefixBySet[String(sourceSetCode).toUpperCase()];
  if (prefix && cleaned.startsWith(prefix) &&
      /^\d+$/.test(cleaned.slice(prefix.length))) {
    return cleanNumber(cleaned.slice(prefix.length));
  }
  return cleaned;
}

/** @param {string} value */
function cleanName(value) {
  return value.normalize('NFKC').replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim().toLowerCase();
}

/**
 * Confirm role labels in the baseline's display names against the engine card.
 * Labels never override the set/collector-number identity gate.
 * @param {string} printedName
 * @param {EngineCard & {attacks?:{name:string}[], powers?:{name:string}[], tags?:string[], energyType?:number}} card
 * @returns {'literal'|'qualified'|null}
 */
function comparePrintedName(printedName, card) {
  if (cleanName(printedName) === cleanName(card.name)) return 'literal';

  const basicEnergy = /^Basic (.+ Energy)$/i.exec(printedName);
  if (basicEnergy && cleanName(basicEnergy[1]) === cleanName(card.name) && card.energyType === 0) {
    return 'qualified';
  }

  const annotated = /^(.*) \(([^()]+)\)$/.exec(printedName);
  if (annotated && cleanName(annotated[1]) === cleanName(card.name)) {
    const qualifier = cleanName(annotated[2]);
    if (qualifier === 'ace spec' && card.tags?.includes('Ace Spec')) return 'qualified';
    if (qualifier === 'fusion strike' && card.tags?.includes('Fusion Strike')) return 'qualified';
    if (card.attacks?.some(attack => cleanName(attack.name) === qualifier)) return 'qualified';
    if (card.powers?.some(power => cleanName(power.name) === qualifier)) return 'qualified';
  }
  return null;
}

/**
 * Exact-print name alias, audited against the bundled paper source rule:
 * xy4-92 is the Item "Battle Compressor Team Flare Gear", whose printed
 * effect searches for up to three cards to discard and then shuffles.
 * Pinned Twinleaf labels that same PHF 92 implementation "Battle Compressor".
 * This is print/name correspondence only, not effect-behavior certification.
 *
 * @param {PrintedEntry} entry
 * @param {EngineCard} card
 * @returns {boolean}
 */
function isVerifiedPrintNameAlias(entry, card) {
  return entry.printId === 'xy4-92' &&
    cleanName(entry.name) === 'battle compressor team flare gear' &&
    cleanName(card.name) === 'battle compressor' &&
    String(card.set).toUpperCase() === 'PHF' &&
    cleanNumber(card.setNumber) === '92';
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
  const sourceSetCode = paperSetCodes.get(sourceSetId);
  const sourceNumber = sourceSetCode
    ? normalizePromoPrintNumber(entry.printId.slice(dash + 1), sourceSetCode)
    : cleanNumber(entry.printId.slice(dash + 1));
  if (!sourceSetCode) {
    return { ...entry, sourceSetCode: null, status: 'unmapped_set', matches: [] };
  }

  const samePrint = cards.filter(card =>
    String(card.set).toUpperCase() === sourceSetCode.toUpperCase() &&
    cleanNumber(card.setNumber) === sourceNumber);
  const exact = samePrint.filter(card =>
    comparePrintedName(entry.name, card) || isVerifiedPrintNameAlias(entry, card));
  const matches = exact.length ? exact : samePrint;
  const relation = exact.length === 1 ? (
    comparePrintedName(entry.name, exact[0]) ||
    (isVerifiedPrintNameAlias(entry, exact[0]) ? 'qualified' : null)
  ) : null;
  const status = exact.length === 1 ? (relation === 'literal' ? 'exact' : 'qualified_exact') :
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
 * Printed promos use PTCGO labels PR-XY / PR-SM, while Twinleaf names their
 * actual implemented sets XYP / SMP. Both overrides are checked against the
 * printed set IDs rather than broad fuzzy card-name matching.
 *
 * @param {{id:string,ptcgoCode?:string}[]} sets
 * @returns {Map<string,string>}
 */
function makePaperSetCodes(sets) {
  const byId = new Map(sets.filter(s => s.ptcgoCode)
    .map(s => [s.id, s.ptcgoCode]));
  for (const [id, sourceCode, engineCode] of [
    ['xyp', 'PR-XY', 'XYP'],
    ['smp', 'PR-SM', 'SMP']
  ]) {
    if (byId.get(id) === sourceCode) {
      byId.set(id, engineCode);
    }
  }
  return byId;
}

/**
 * @returns {Record<string, ReturnType<typeof matchPaperPrint>[]>}
 */
function auditAichiBaselines() {
  const markdown = fs.readFileSync(path.join(ROOT, 'results/competitive_deck_baselines/README.md'), 'utf8');
  const decks = parseBaselineDecks(markdown);
  const sets = JSON.parse(fs.readFileSync(path.join(ROOT, 'resources/sets/en.json'), 'utf8'));
  const paperSetCodes = makePaperSetCodes(sets);
  const implemented = loadImplementedCards();
  return Object.fromEntries(Object.entries(decks).map(([name, entries]) =>
    [name, entries.map(entry => matchPaperPrint(entry, paperSetCodes, implemented))]));
}

module.exports = {
  parseBaselineDecks, cleanNumber, normalizePromoPrintNumber, cleanName,
  makePaperSetCodes, comparePrintedName, isVerifiedPrintNameAlias,
  matchPaperPrint, loadImplementedCards, auditAichiBaselines
};
