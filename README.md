# Litmus MCP Server

Model Context Protocol (MCP) server for Litmus experiment intake, validation, routing, and submission.

## Overview

This MCP server allows AI assistants (Claude, ChatGPT, etc.) to:
- Draft experiment intakes from natural language
- Validate intakes against the schema
- Route experiments to best-fit labs
- Submit experiments and manage attachments
- Find candidate labs, get cost estimates, and create real orders against the
  live litmus-project backend (`litmus_get_cro_match`, `litmus_calculate_estimate`,
  `litmus_create_order` — see "Live Backend Tools" below)

## Installation

```bash
pip install litmus-mcp
```

Or install from source:

```bash
git clone https://github.com/litmus-science/litmus-mcp.git
cd litmus-mcp
pip install -e .
```

## Running the Server

```bash
litmus-mcp
```

Or run as a module:

```bash
python -m litmus_mcp.server
```

## Configuration

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "litmus": {
      "command": "litmus-mcp"
    }
  }
}
```

### Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "litmus": {
      "command": "litmus-mcp"
    }
  }
}
```

### Environment variables (for the Live Backend Tools)

`litmus_get_cro_match`, `litmus_calculate_estimate`, and `litmus_create_order` call
a real litmus-project backend over HTTP instead of local mock data. Configure them
via an `env` block:

```json
{
  "mcpServers": {
    "litmus": {
      "command": "litmus-mcp",
      "env": {
        "LITMUS_API_BASE": "http://localhost:8000",
        "LITMUS_API_KEY": "lk_xxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

- `LITMUS_API_BASE` — optional, defaults to `http://localhost:8000`. Point this at
  staging/production to use a deployed backend instead of a local one.
- `LITMUS_API_KEY` — optional overall, but **required** for `litmus_calculate_estimate`
  and `litmus_create_order` (both act on an authenticated account). Obtain one by
  calling `POST /auth/register` on your litmus-project backend — the key is returned
  once in that response and never re-exposed afterward, so save it immediately.
  `litmus_get_cro_match` works with no key configured, since its backend endpoint
  is public.

## Tools

### intake.draft_from_text
Convert natural language to a structured intake JSON.

```json
{
  "text": "I want to test if my new compound kills cancer cells",
  "experiment_type_hint": "CELL_VIABILITY_IC50"
}
```

### intake.validate
Validate an intake against the schema.

```json
{
  "intake": { ... },
  "strict": false
}
```

### intake.suggest_questions
Get questions to improve intake completeness.

```json
{
  "intake": { ... },
  "target_completeness": 0.7,
  "max_questions": 3
}
```

### routing.match_labs
Route an intake to best-fit labs.

```json
{
  "intake": { ... },
  "top_k": 3,
  "strict_deliverables": false,
  "region_preference": "US"
}
```

### labs.search
Search labs with filters.

```json
{
  "experiment_type": "CELL_VIABILITY_IC50",
  "max_bsl": "BSL2",
  "region": "US"
}
```

### labs.get
Get a specific lab profile.

```json
{
  "lab_id": "lab_cellassay_pro_001"
}
```

### intake.submit
Submit a validated intake.

```json
{
  "intake": { ... },
  "selected_lab_id": "lab_cellassay_pro_001"
}
```

### files.create_upload_url
Create a signed URL for file upload.

```json
{
  "filename": "compound_sds.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 102400
}
```

### files.attach_to_intake
Attach an uploaded file to a submission.

```json
{
  "submission_id": "sub_abc123",
  "file_id": "file_xyz789",
  "attachment_type": "SDS"
}
```

## Live Backend Tools

Unlike every tool above, these call the real litmus-project backend over HTTP
(see "Environment variables" under Configuration). Errors from the backend
(including a missing `LITMUS_API_KEY`) are returned as a JSON error payload —
e.g. `{"error": "...", "error_type": "missing_api_key" | "backend_error" | "connection_error"}`
— rather than a protocol-level failure.

### litmus_get_cro_match
Find candidate labs/CROs via the backend's lab directory. **This is a first-pass
backend endpoint** — server-side filtering by `assay_type`/`criteria` isn't
implemented yet, so it returns every lab in the network unconditionally, unranked
and unfiltered. For local scoring against mock lab data with real filtering, use
`routing.match_labs` instead. No `LITMUS_API_KEY` required.

```json
{
  "assay_type": "CELL_VIABILITY_IC50",
  "criteria": { "region": "US" }
}
```

### litmus_calculate_estimate
Get a cost and turnaround-time estimate for an experiment spec. Requires
`LITMUS_API_KEY`. Does not create or persist anything.

```json
{
  "intake": { "experiment_type": "CELL_VIABILITY_IC50" }
}
```

### litmus_create_order
Submit a real, persisted order request. Requires `LITMUS_API_KEY` — the submitter
identity is derived server-side from the authenticated account and cannot be set
via arguments. May trigger downstream notification/PDF generation on the backend.

```json
{
  "raw_payload": { "experiment_type": "CELL_VIABILITY_IC50" }
}
```

## Resources

The server exposes these resources:

- `litmus://schemas/experiment_intake` - Experiment intake JSON Schema
- `litmus://schemas/lab_profile` - Lab profile JSON Schema
- `litmus://taxonomy/deliverables` - Deliverables taxonomy
- `litmus://rubric/routing_weights` - Current routing weights

## Development

```bash
# Clone the repo
git clone https://github.com/litmus-science/litmus-mcp.git
cd litmus-mcp

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Test with MCP Inspector
npx @modelcontextprotocol/inspector litmus-mcp
```

## License

MIT
