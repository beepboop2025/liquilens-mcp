# LiquiLens MCP — the Failure Radar as agent tools

**Endpoint:** `https://api.liquilens.in/mcp` (streamable HTTP, no auth, no install)

LiquiLens is a failure early-warning system for banks and lenders, built on public
data with the validation record served beside every claim. This MCP server lets any
LLM agent read the same record a human sees.

## Add it

Claude Code:

    claude mcp add --transport http liquilens https://api.liquilens.in/mcp

Claude.ai / ChatGPT / Cursor: add a custom connector or MCP server with the URL above.

## Tools

| Tool | What it serves |
|---|---|
| `failure_radar_board` | The live board: every Indian lender with a fresh vetted dossier — failure PD term structure (12/24/36m), RBI action-zone status, funding fragility, market distance to default, watchlist tier under a published rule |
| `failure_radar_institution` | One institution in depth: PD trajectory with drivers, PCA/SAF headroom history, forensic screen, market reading |
| `evidence_markets` | The validation record per market, one headline each |
| `evidence_india` | The Indian record: 48 institutions across two decades, misses and false alarms included |
| `evidence_institution` | One Indian institution's full crisis replay with sourced quarterly rows |
| `evidence_us` | The US record: 550 FDIC failures since 2008, 73.1% recall at 21.7-month median lead, marquee replays including the honest fraud miss |
| `evidence_europe` | Seven audited European case files, Northern Rock to Credit Suisse, replayed through unrecalibrated lenses |
| `universe_search` | RBI's official registered-NBFC registry (9,000+ entries) |
| `rbi_supervisory_tape` | Latest RBI enforcement actions, each linking to the RBI's own page |
| `verify_published_record` | Independent cryptographic verification of the as-published record |

## The governance line

The generative layer explains; **only the validated deterministic layer scores.**
Numbers come from deterministic engines with model cards, never from a model.
Screens, not ratings; not investment advice. Institutions without a vetted dossier
are absent by design — the tools say so rather than inventing a score.

## Siblings from the same lab

- [Seiche](https://api.seiche.info/mcp) — US money-market funding stress (the plumbing)
- [groundcheck](https://groundcheck.seiche.info) — claim grounding and citation verification
- Palimpsest (`https://api.seiche.info/palimpsest/mcp`) — live internet-censorship signals
- [Undertow](https://liquilens.in/undertow/) — the cross market liquidity map: daily tiered board, exit cost at position size, Telegram front door at [t.me/undertow_LiquiLens_bot](https://t.me/undertow_LiquiLens_bot)

Product: [liquilens.in](https://liquilens.in) · Live demo: [demo.liquilens.in](https://demo.liquilens.in)
