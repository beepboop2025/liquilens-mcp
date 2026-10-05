# LiquiLens MCP — the Failure Radar as agent tools

**Endpoint:** `https://api.liquilens.in/mcp` (streamable HTTP, no auth, no install)

LiquiLens is the institution-evidence product of **LIQUILENS PRIVATE LIMITED**,
a registered company in India (CIN **U62011RJ2026PTC116792**). One company, three
connected products: LiquiLens investigates institutions, Seiche explains funding
conditions, and Undertow examines market liquidity. People and AI agents can
follow an exposure across all three while retaining each product's source dates,
coverage gaps and research limits. International access does not imply universal
market coverage or a shared score.

Read the [company and investor story](https://liquilens.in/investors/) and the
[shared company profile](https://liquilens.in/company-profile.json).

**Try it live:** [liquilens.in/developers](https://liquilens.in/developers/) ·
**REST catalog:** [api.liquilens.in/api](https://api.liquilens.in/api)

LiquiLens is a failure early-warning system for banks and lenders, built on public
data with a machine-readable historical-evidence boundary served beside every claim.
This MCP 1.8.1 endpoint exposes 23 read-only tools and 5 guided prompts so an agent
reads the same status, eligibility flags and cited record a human sees. Its
capability inventory is pinned to LiquiLens commit
`d6f99bdf2de14e8ef2f29032cf9561ca8a446de8`.

It now reads both ends of the chain: which institutions are fragile, and whether that
stress is actually crossing into the real economy: companies rolling paper and drawing
credit lines, households falling behind. Channels that cannot be read are named in
`cannot_see` rather than reported as calm.

## Add it

For Hermes and OpenClaw, use the native setup guides:

- [Hermes: configuration, connection checks and a first research task](https://liquilens.in/agents/hermes/)
- [OpenClaw: configuration, discovery checks and a first research task](https://liquilens.in/agents/openclaw/)

The current guides select thirteen research tools across LiquiLens, Seiche and
Undertow, including GIFT City, reference FX and gold scenarios. Their dated
native-client receipts retain the original nine-tool selection and exact
verification scope. Public research requires no account or API key; fair-use
limits apply and your model provider may charge separately.

The [free starter kit](https://liquilens.in/agents/) also includes a Python brief,
a manual n8n funding workflow and configurations for the clients below.

OpenClaw users can also install the optional research instructions from
[ClawHub](https://clawhub.ai/beepboop2025/skills/liquilens-trading-research):

```sh
openclaw skills install @beepboop2025/liquilens-trading-research --version 1.1.0
```

Connect the MCP servers using the OpenClaw guide first. The skill supplies task
instructions and a configuration template; installation does not configure servers
or run research. Its [source bundle](skills/liquilens-trading-research/) is MIT-0;
that license does not relicense source data or API responses.

Checked on 4 October 2026 (UTC): version 1.1.0 is public and ClawHub's
[version-pinned verification result](https://clawhub.ai/api/v1/skills/liquilens-trading-research/verify?ownerHandle=beepboop2025&version=1.1.0)
reports a passed security check with a benign, high-confidence verdict.
Its embedded detailed scanner report retains
seven findings, including medium external-transmission flags for the public MCP
URLs, and reports partial analysis. Review the [versioned security audit](https://clawhub.ai/beepboop2025/skills/liquilens-trading-research/security-audit?version=1.1.0)
before installation and use public research inputs.
Its isolated Linux install recorded the correct version and matched all
three reviewed source files. ClawHub's public verifier and the installed Linux
client's version-pinned `openclaw skills verify` now both report `pass`, with the
generated Skill Card present. The upload is unsigned and has no server-resolved
GitHub import provenance. A fresh isolated macOS install after storage recovery
also matched all three source-file hashes, and its version-pinned verification
reports `pass`. The earlier macOS timeout remains a separate failed attempt.
No model or research tool ran in these checks.
The direct MCP configuration is available independently of the ClawHub skill.

Claude Code:

    claude mcp add --transport http liquilens https://api.liquilens.in/mcp

Codex:

    codex mcp add liquilens --url https://api.liquilens.in/mcp

Cursor: merge the [remote MCP config](https://liquilens.in/developers/recipes/cursor-mcp.json)
into `.cursor/mcp.json` for one project or `~/.cursor/mcp.json` for all projects.
The download includes the companion Seiche funding endpoint. Preserve existing entries.
For an existing Codex config, use the [TOML snippet](https://liquilens.in/developers/recipes/codex-mcp.toml)
and merge its server entries into `~/.codex/config.toml`.

Claude.ai / ChatGPT: add a custom connector or MCP app with the endpoint above where
that feature is available in your workspace.

This repository is the public discovery and documentation mirror. The hosted
implementation is maintained in a private core repository. This public mirror pins
its inspectable capability contract to the reviewed source revision above.
The [official Registry entry](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.beepboop2025%2Fliquilens/versions/latest)
uses the name `io.github.beepboop2025/liquilens`. This repository's Registry
metadata revision 1.8.1 points to the public mirror and free starter kit.
The hosted MCP now reports version 1.8.1 at the same endpoint. The Registry
metadata and runtime happen to share a version number; they remain separately
verified contracts. The pinned source and tool inventory above describe the current
runtime. The existing Registry record continues to identify this public mirror.

The current runtime separates fresh model results from reviewed filing facts:
expired filing scores are excluded from the live board, current disclosures retain
their official source and publication clocks, and inactive institutions remain
identifiable in historical evidence. Its US evidence includes the June 2026 panel
and reviewed 2026 failure notices through 25 September.

## Query source histories

The separate [source-data MCP and Python client](source-data.md) expose funding histories, bank filings and Bitcoin/Liquid settlement observations with source receipts, native units and capture clocks. Use the [live coverage table](https://liquilens.in/agents/#source-data) or import its [OpenAPI contract](https://api.seiche.info/api/v2/research-data/openapi.json).

## Run a research task

The [research recipes](https://liquilens.in/developers/#research-recipes) run with
Python 3.11+ and its standard library. No API key, LLM or Python package install is needed.
[Download and inspect `financial_research.py`](https://liquilens.in/developers/recipes/financial_research.py),
then run:

```sh
python3 financial_research.py bank-review
python3 financial_research.py bank-review --slug cosmos-ucb
python3 financial_research.py funding-brief
```

The first command discovers covered bank slugs. The second checks coverage before
retrieving that exact bank's sourced asset-quality history; an absent slug stays
`not_covered`. The funding brief calls Seiche's money-market desk. Returned evidence
retains its native source dates, eligibility, unavailable states and limitations;
a successful request does not imply fresh or complete evidence. Each run is bounded
and performs no scheduling or trading. Operators should add `--verification` so their
checks are labelled synthetic and excluded from adoption totals.

For a visual workflow, [download the n8n bank-review workflow](https://liquilens.in/developers/recipes/n8n-bank-review.json)
and follow the [import guide](https://liquilens.in/developers/recipes/n8n-bank-review.md).
It uses a manual trigger and no LLM. The guide records its execution-verification status;
a downloadable workflow does not imply acceptance into n8n's template library.

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
| `bank_asset_quality_review` | Exact-slug bank review with sourced GNPA/NNPA history, percentage-point changes, distinct PCR definitions and capital/supervisory scope; no new score or credit approval |
| `bank_npa_reconciliation` | Arithmetic check of a complete caller-supplied NPA movement table; keeps cash recoveries, write-offs, sales and upgrades distinct without authenticating the input |
| `banking_specialisation_coverage` | Discover covered Indian commercial, small finance and urban cooperative banks, with observed, stale, historical and absent evidence distinguished; not a census or rating |
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
| `institution_research_coverage` | Discover institution dossiers, registry entries and reviewed filing facts with separate observed, stale, historical, subset and registry-only states; coverage is not a rating or permission to trade |
| `institution_review_packet` | One lender's deterministic evidence packet for human review, with coverage and freshness stated explicitly |
| `latest_article` | Today's exact evidence-led LiquiLens article, or a labelled historical replay when the evidence did not move |
| `rbi_supervisory_tape` | Latest RBI enforcement actions, each linking to the RBI's own page |
| `research_network` | Bounded source discovery for connected Palimpsest, Seiche and Undertow research with availability and evidence boundaries intact |
| `stablecoin_rails_board` | Issuer peg, redemption-run, chain-concentration and rail tripwire state; missing data never becomes `CALM` |
| `universe_search` | RBI's official registered-NBFC registry (9,000+ entries) |
| `verify_published_record` | Independent cryptographic verification of the as-published record |

## Prompts

| Prompt | Guided playbook |
|---|---|
| `bank_asset_quality_brief` | Discover an exact bank slug, review cited NPA history and capital scope, then reconcile only a complete disclosed movement table; preserve stale/missing evidence and supervisory gaps |
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

## Quant research agent integrations

[Native framework tools and cited quant pipeline captures](https://liquilens.in/agents/quant/) connect Seiche funding, LiquiLens bank diagnostics and Undertow market liquidity through compact read-only tables. LangChain/LangGraph, CrewAI, OpenAI Agents and Pydantic AI share one evidence contract and repeat-call revision tokens. Current published history is not an as-published vintage archive. No execution authority or institutional-adoption claim is implied.
