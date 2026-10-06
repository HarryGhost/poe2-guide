// Actual extraction method used in this run, executed through Codex cua_repl.
// DOM-backed public script only. No cookies, browser storage or runtime globals.
// The captureRoot must be a newly created directory. tab is the bound task tab.
async function extractPublicDocument(tab, captureRoot, filename) {
  const readChunk = ({offset, size}) => {
    const script = Array.from(document.scripts).find(s =>
      s.textContent.startsWith('window.__PRELOADED_STATE__='));
    if (!script) throw new Error('Public preloaded document script not present');
    const state = JSON.parse(script.textContent
      .slice('window.__PRELOADED_STATE__='.length).replace(/;\s*$/, ''));
    const query = state.poe2State.apollo.graphqlV2.queries.find(q =>
      q.queryKey[0] === 'ngf-ug-featured-document-page');
    const document = query.state.data[0].game.documents.userGeneratedDocumentBySlug;
    // Serialize inside the DOM evaluator to avoid transport object-depth loss.
    const serialized = JSON.stringify(document);
    return size === 0 ? serialized.length : serialized.slice(offset, offset + size);
  };
  const length = await tab.playwright.evaluate(readChunk, {offset: 0, size: 0});
  let serialized = '';
  for (let offset = 0; offset < length; offset += 80000) {
    serialized += await tab.playwright.evaluate(readChunk, {offset, size: 80000});
  }
  // The actual run read large strings in 80,000-character DOM-backed chunks.
  // Saving only this document avoids unrelated queries, comments or account data.
  const fs = await import('node:fs/promises');
  await fs.writeFile(captureRoot + '/evidence/public-data/' + filename,
    JSON.stringify(JSON.parse(serialized), null, 2));
}
// normalize_capture.py then retains only requested branches and relevant author
// sections; strips ads, comments, account/live-character widgets and loot filters.
