'use strict';
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '../..');
const LABELS = {'runner-up':'vileplume','champion':'shadow_rider','10th place':'regidrago','fifth place':'mew_genesect'};
/** Parse exact print/count rows from the four independently checked Aichi decklists. @param {string} markdown @returns {Array<object>} */
function parseDecks(markdown) {
  const headings = [...markdown.matchAll(/^## ([^\r\n]+)$/gm)];
  const decks = [];
  for (let i = 0; i < headings.length; i++) {
    const label = Object.keys(LABELS).find(k => headings[i][1].toLowerCase().includes(k));
    if (!label) continue;
    const end = headings[i + 1] ? headings[i + 1].index : markdown.length;
    const cards = [];
    for (const line of markdown.slice(headings[i].index, end).split(/\r?\n/)) {
      if (!line.startsWith('|')) continue;
      const col = line.split('|').slice(1, -1).map(c => c.trim().replace(/^`|`$/g, ''));
      if (/^\d+$/.test(col[0]) && /^[a-z0-9]+-[a-zA-Z0-9]+$/.test(col[2])) {
        cards.push({quantity: Number(col[0]), name: col[1], print_id: col[2]});
      }
    }
    if (cards.reduce((n,c) => n + c.quantity, 0) !== 60 || new Set(cards.map(c => c.print_id)).size !== cards.length) {
      throw new Error('Invalid 60-card baseline: ' + headings[i][1]);
    }
    decks.push({id: LABELS[label], heading: headings[i][1], cards});
  }
  if (decks.length !== 4 || new Set(decks.map(d => d.id)).size !== 4) throw new Error('Expected 4 unique Aichi baseline decks');
  return decks;
}
/** @returns {Array<object>} */
function loadDecks() { return parseDecks(fs.readFileSync(path.join(ROOT, 'results/competitive_deck_baselines/README.md'), 'utf8')); }
module.exports = {parseDecks, loadDecks, ROOT};
