# LiquiLens MCP | Bank and lender failure-risk tools

**Endpoint:** `https://api.liquilens.in/mcp` (streamable HTTP, no auth, no install)

**Try it live:** [liquilens.in/developers](https://liquilens.in/developers/) ·
**REST catalog:** [api.liquilens.in/api](https://api.liquilens.in/api)

LiquiLens is an early-warning system for bank and lender distress, built from public
data with validation evidence published beside its claims. This MCP server exposes
the same record as structured tools.

The tools cover institution risk and signs that funding stress is reaching companies or
households. Unavailable channels are listed in `cannot_see` rather than reported as calm.

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
| `evidence_us` | The US record: 552 FDIC failures since 2008, 72.8% recall at 21.7-month median lead, marquee replays including the honest fraud miss |
| `evidence_europe` | Seven audited European case files, Northern Rock to Credit Suisse, replayed through unrecalibrated lenses |
| `universe_search` | RBI's official registered-NBFC registry (9,000+ entries) |
| `rbi_supervisory_tape` | Latest RBI enforcement actions, each linking to the RBI's own page |
| `verify_published_record` | Independent cryptographic verification of the as-published record |
| `corporate_transmission_board` | Is funding stress reaching nonfinancial firms? The commercial-paper market, bank credit lines, real-economy confirmation (claims, capex, inventories, openings, business bankruptcies) and a balance-sheet context channel, with a TRANSMITTING/CONTAINED verdict |
| `household_credit_board` | Is stress transmitting through household balance sheets? Fed delinquency and charge-off legs against each leg's own trailing decade, two-sided revolving-credit velocity, debt service as unscored context |
| `forward_odds` | Counted forward stress odds for each public-signal layer, withheld until the layer has enough observed history |
| `institution_review_packet` | One lender's deterministic evidence packet for human review, with coverage and freshness stated explicitly |

## Scoring boundary

The generative layer explains; **only the validated deterministic layer scores.**
Numbers come from deterministic engines with model cards, never from a model.
Screens, not ratings; not investment advice. Institutions without a vetted dossier
are absent by design — the tools say so rather than inventing a score.

## Siblings from the same lab

- [Seiche](https://api.seiche.info/mcp): US dollar funding stress
- [Groundcheck](https://groundcheck.seiche.info): live-source claim and citation verification
- Palimpsest (`https://api.seiche.info/palimpsest/mcp`): internet-censorship signals
- [Undertow](https://liquilens-undertow.com/developers/): market-liquidity tiers and estimated exit cost by position size

Product: [liquilens.in](https://liquilens.in). The [interactive demo](https://demo.liquilens.in) requires sign-in and is available by request.
