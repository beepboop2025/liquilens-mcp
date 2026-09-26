# Funding, filing and settlement source data

This separate public MCP endpoint serves source histories used alongside Seiche, LiquiLens and Undertow:

`https://api.seiche.info/api/v2/research-data/mcp`

[Browse current coverage and copy a client configuration](https://liquilens.in/agents/#source-data). No account or API key is required. Import the [OpenAPI 3.1 contract](https://api.seiche.info/api/v2/research-data/openapi.json) for REST tools.

| Tool | Use |
| --- | --- |
| `research_catalog` | Discover datasets, native cadence, coverage and source restrictions. |
| `research_series` | Find a series and its native unit before querying values. |
| `research_entities` | Resolve explicit FDIC or NCUA identifiers. |
| `research_observations` | Read a bounded page of dated values, receipt references and capture clocks. |
| `research_tracked_institutions` | Inspect institution coverage without assuming registry membership means financial coverage. |
| `research_analysis` | Read descriptive comparisons; unknown units are excluded from incompatible aggregations. |

The catalog currently spans OFR funding/repo/yield datasets, FDIC and NCUA filings, selected reviewed Indian issuer filings, and Bitcoin/Liquid settlement observations. Coverage is dynamic: query the catalog instead of treating a download count as a fixed coverage promise.

## First history query

Download and inspect the [starter kit](https://liquilens.in/agents/trading-research-kit.zip), check its [manifest](https://liquilens.in/agents/manifest.json), then run with Python 3.11+:

```sh
python3 source_data.py catalog --product seiche
python3 source_data.py series --dataset ofr-fnyr --q SOFR --limit 10
python3 source_data.py observations --dataset ofr-fnyr --series FNYR-SOFR-A --start 2026-09-01 --limit 100
python3 source_data.py entities --dataset fdic-financials --q JPMorgan --limit 10
```

The client needs only the standard library. Follow `next_offset` explicitly. Maximum page size is 10,000 observations and 500 tracked institutions; smaller pages are useful for agent context budgets.

An observation date is distinct from its capture date. `--as-known-at` selects captured vintages; it cannot reconstruct point-in-time knowledge before the first capture. Nulls, unavailable responses, native units and publication restrictions are part of the evidence. Data access does not confer scoring, execution or training authority. Operator checks should pass `--verification`; they do not count as adoption.

Runtime version: 1.1.0. Hosted implementation source: `3273d7d0f7ce8457651ab54b6c650fe98a982d64`. This public repository supplies discovery and runnable-client documentation; the server is maintained in the private fleet repository. Registry metadata is in [research-data-server.json](research-data-server.json).
