# Litmus Science MCP Server

Order real lab experiments from Claude, ChatGPT, Cursor, or any MCP client. Describe what you want to find out in plain language; [Litmus Science](https://litmus.science) matches it to the assays it offers, collects what a lab needs, and routes the request to vetted CROs, cloud labs, and university core facilities for quotes.

> Litmus Science (litmus.science) is not affiliated with Litmus (litmus.com), the email testing company.

**Docs:** [platform.litmus.science/docs/mcp](https://platform.litmus.science/docs/mcp): server URL, sign-in, tools, and worked examples.

## What you can do with it

- **Outsource an assay without a wet lab:** binding (SPR / BLI), ITC, thermal shift, biochemical HTS, ELISA, qPCR, cell viability, cell-based potency, ADME / Tox, and more.
- **Validate AI-designed binders:** VHH / nanobodies, minibinders, and peptides, with binder calls and affinity per design.
- **Give an AI agent or co-scientist a wet lab:** the agent drafts the request, fills in requirements with you, and submits it.
- **Get quotes from multiple labs with one request:** one contract and one invoice across labs.

Example prompts:

```
Get SPR kinetics run on 12 VHH designs against my target. I have purified protein.
Find a CRO to measure microsomal stability and CYP inhibition for 8 compounds.
I designed 96 minibinders. How do I validate which ones actually bind?
```

## Connect

Litmus runs a hosted MCP server: connect over Streamable HTTP and sign in to Litmus with OAuth. You choose which tools the client may use.

Setup, the server URL, authentication, and consent are covered in the [MCP integration guide](https://platform.litmus.science/docs/mcp):

- [Overview](https://platform.litmus.science/docs/mcp)
- [Authentication](https://platform.litmus.science/docs/mcp/authentication)
- [MCP server](https://platform.litmus.science/docs/mcp/server): calling the server, tool reference, order request lifecycle
- [Consent and permissions](https://platform.litmus.science/docs/mcp/consent-and-permissions)

## Tools

| Tool | What it does |
| --- | --- |
| `create_order_request` | Start a draft order request from a scientific objective in your own words, plus any context (molecule, material in hand, timelines, prior results). Litmus suggests the assays the objective needs, each with its purpose and typical market pricing. |
| `update_order_request` | Confirm which suggested assays to keep, then supply answers to anything still missing (requirements, lab location, budget, turnaround). Returns what's still needed until the request is `submittable`. |
| `submit_order_request` | Submit a `submittable` order request for lab matching and quotes. |
| `get_order_request` | Read an order request's current state by its `order_request_id`, to resume it later. |
| `whoami` | Show which Litmus user and integration the connection belongs to, and its scopes. |

### Typical flow

1. `create_order_request` with the objective → Litmus suggests assays.
2. You pick the assays to keep → `update_order_request` with `confirm_assays`.
3. Answer each item in `readiness.missing` → `update_order_request` until status is `submittable`.
4. Review the summary and `submit_order_request`.

## What happens after you submit

You get a copy of the request by email. Litmus reviews it and asks labs that can run it for quotes, and emails you when the first quote arrives. On the order request's page you compare quotes, pick a lab, and sign the standard agreements so the work can start. Suggested assay pricing is a market estimate, not a quote.

## Pricing

See [litmus.science/pricing](https://litmus.science/pricing/). Arrayed binding has published, volume-based pricing; custom experiments are the lab's quote plus a Litmus fee, shown before you commit.

## Data and IP

Protocols, results, and IP belong to you by default. Litmus does not sell research data. See the [privacy policy](https://litmus.science/privacy.html).

## Links

- Website: https://litmus.science
- Assay catalog: https://litmus.science/assays/
- Walkthrough: [How to give your AI agent a wet lab](https://litmus.science/blog/give-your-ai-agent-a-wet-lab.html)
- Start a request on the web: https://platform.litmus.science/intake
- Contact: hello@litmus.science

## Self-hosted server (legacy)

This repository also contains an earlier, locally run MCP server (`intake.*`, `routing.*`, `labs.*`, `files.*` tools) that works against the experiment intake schema. It is kept for reference and development; use the hosted server above to place real orders.

```bash
uvx --from git+https://github.com/litmus-science/litmus-mcp.git litmus-mcp
# or
pip install "git+https://github.com/litmus-science/litmus-mcp.git" && litmus-mcp
```

Development:

```bash
git clone https://github.com/litmus-science/litmus-mcp.git
cd litmus-mcp
pip install -e ".[dev]"
pytest
npx @modelcontextprotocol/inspector litmus-mcp
```

## License

MIT
