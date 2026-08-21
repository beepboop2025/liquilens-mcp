# Contributing to LiquiLens MCP

Thanks for helping make the public LiquiLens connector easier to inspect and use.
This repository is the discovery, documentation, and capability-contract mirror for
the hosted read-only MCP endpoint; the implementation is maintained separately.

## Useful contributions

- correct a broken public link, example, or protocol-compatibility note;
- improve installation or client-connection instructions;
- add a contract test for a documented tool, prompt, boundary, or registry field;
- clarify evidence eligibility, missing-data behavior, or the screens-not-ratings line.

Please do not submit credentials, private institution data, personal data, or requests
that turn the public connector into a write/action surface. Product outputs must remain
research screens rather than ratings, investment advice, or unsupported predictions.

## Validate a change

Use Python 3.12 or newer and run:

```sh
python3 -m unittest discover -s tests -v
```

The live smoke test is optional because it reads the production endpoint:

```sh
python3 scripts/smoke_live_mcp.py
```

Keep pull requests small, explain the user-visible effect, update tests with contract
changes, and run `git diff --check` before pushing. For a vulnerability, use the private
reporting path in [SECURITY.md](SECURITY.md), not a public issue.
