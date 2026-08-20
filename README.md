# LiquiLens MCP — the Failure Radar as agent tools

**Endpoint:** `https://api.liquilens.in/mcp` (streamable HTTP, no auth, no install)

**Try it live:** [liquilens.in/developers](https://liquilens.in/developers/) ·
**REST catalog:** [api.liquilens.in/api](https://api.liquilens.in/api)

LiquiLens is a failure early-warning system for banks and lenders, built on public
data with a machine-readable historical-evidence boundary served beside every claim.
This MCP 1.7.0 endpoint exposes 18 read-only tools and 4 guided prompts so an agent
reads the same status, eligibility flags and cited record a human sees. Its
capability inventory is pinned to LiquiLens commit
`5628b41bd9ef1e753dafba72e29b6b303ec18e3d`.

It now reads both ends of the chain: which institutions are fragile, and whether that
stress is actually crossing into the real economy: companies rolling paper and drawing
credit lines, households falling behind. Channels that cannot be read are named in
`cannot_see` rather than reported as calm.

## Add it

Claude Code:

    claude mcp add --transport http liquilens https://api.liquilens.in/mcp

Claude.ai / ChatGPT / Cursor: add a custom connector or MCP server with the URL above.

This repository is the discovery and documentation mirror. The signed implementation
and registry manifest live in the
[LiquiLens core repository](https://github.com/beepboop2025/LiquiLens). The official
registry currently serves
[`io.github.beepboop2025/liquilens` version 1.7.0](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.beepboop2025%2Fliquilens/versions/latest).

## Protocol compatibility

- `2026-07-28`: stateless requests use `server/discover`, per-request `_meta`,
  `MCP-Protocol-Version`, and mirrored `Mcp-Method` / `Mcp-Name` routing headers.
- `2025-11-25`, `2025-06-18`, and `2025-03-26`: retained legacy initialization,
  tools, prompts, notifications, batching, and ping behavior.
- Tools, prompts, and discovery responses are deterministic. Modern list responses
  carry public cache metadata.
- `resources/list` and `resources/templates/list` are supported and currently return
  empty catalogs. `resources/read` returns an explicit not-found error instead of
  inventing a resource.

## Tools

| Tool | What it serves |
|---|---|
| `corporate_transmission_board` | Is funding stress reaching nonfinancial firms? The commercial-paper market, bank credit lines, real-economy confirmation (claims, capex, inventories, openings, business bankruptcies) and a balance-sheet context channel, with a TRANSMITTING/CONTAINED verdict |
| `crypto_exposure_board` | Cited bank/crypto exposure register joined to Undertow run-risk context; display-only, never an institution score |
| `crypto_regime_board` | Compact BTC/ETH change-point state and its display-only cross-read against disclosed bank exposure |
| `evidence_europe` | `NAMED_CASE_FILES_CONSTRUCTION_PIT`: seven audited case files, deliberately no cohort claim; both eligibility flags false |
| `evidence_india` | `PERIOD_END_PROXY_CONSTRUCTION_PIT`: 48 institutions across two decades, misses and false alarms included; both eligibility flags false |
| `evidence_institution` | One Indian institution's construction-PIT crisis replay with sourced quarterly rows |
| `evidence_markets` | Historical-evidence status for all three markets, with `validated_backtest_eligible` and `real_money_eligible` served explicitly |
| `evidence_us` | `CURRENT_AMENDED_CONSTRUCTION_PIT`: 552 FDIC failures since 2008, 72.8% recall, 21.7-month median lead and AUC 0.854; both eligibility flags false |
| `failure_radar_board` | The live board: every Indian lender with a fresh vetted dossier, including failure PD term structure (12/24/36m), RBI action-zone status, funding fragility, market distance to default, and watchlist tier under a published rule |
| `failure_radar_institution` | One institution in depth: PD trajectory with drivers, PCA/SAF headroom history, forensic screen, market reading |
| `forward_odds` | Counted forward stress odds for each public-signal layer, withheld until the layer has enough observed history |
| `household_credit_board` | Is stress transmitting through household balance sheets? Fed delinquency and charge-off legs against each leg's own trailing decade, two-sided revolving-credit velocity, debt service as unscored context |
| `institution_review_packet` | One lender's deterministic evidence packet for human review, with coverage and freshness stated explicitly |
| `latest_article` | Today's exact evidence-led LiquiLens article, or a labelled historical replay when the evidence did not move |
| `rbi_supervisory_tape` | Latest RBI enforcement actions, each linking to the RBI's own page |
| `stablecoin_rails_board` | Issuer peg, redemption-run, chain-concentration and rail tripwire state; missing data never becomes `CALM` |
| `universe_search` | RBI's official registered-NBFC registry (9,000+ entries) |
| `verify_published_record` | Independent cryptographic verification of the as-published record |

## Prompts

| Prompt | Guided playbook |
|---|---|
| `crypto_liquidity_briefing` | BTC/ETH regime, stablecoin rails, and disclosed bank links in one display-only evidence pack |
| `failure_radar_briefing` | Board-level institution risk with transmission context from the public US signal layers |
| `institution_health_check` | One lender health check with the historical-evidence boundary and uncertainty attached |
| `stress_evidence_pack` | Region-specific evidence for India, the United States, Europe, or the cross-market summary |

## The governance line

The generative layer explains; **deterministic screening policy scores.** Historical
diagnostics retain their served evidence status and eligibility flags and do not become
validated-backtest or real-money evidence merely because a deterministic engine produced
them. Screens, not ratings; not investment advice. Institutions without a vetted dossier
are absent by design — the tools say so rather than inventing a score.

The three historical status tokens are part of the API contract, not marketing copy:
`PERIOD_END_PROXY_CONSTRUCTION_PIT` for India,
`CURRENT_AMENDED_CONSTRUCTION_PIT` for the United States, and
`NAMED_CASE_FILES_CONSTRUCTION_PIT` for Europe. In the current release, every market
serves `validated_backtest_eligible: false` and `real_money_eligible: false`.

## Siblings from the same lab

- [Seiche](https://api.seiche.info/mcp) — US money-market funding stress (the plumbing)
- [groundcheck](https://groundcheck.seiche.info) — claim grounding and citation verification
- Palimpsest (`https://api.seiche.info/palimpsest/mcp`) — live internet-censorship signals
- [Undertow](https://liquilens-undertow.com/developers/) — the cross market liquidity map: daily tiered board, exit cost at position size, Telegram front door at [t.me/undertow_LiquiLens_bot](https://t.me/undertow_LiquiLens_bot)

Product: [liquilens.in](https://liquilens.in) · Live demo: [demo.liquilens.in](https://demo.liquilens.in)
