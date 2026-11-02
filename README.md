# Litmus Science MCP Server

Model Context Protocol (MCP) server for [Litmus Science](https://litmus.science) experiment intake, validation, routing, and submission.

## Overview

This MCP server allows AI assistants (Claude, ChatGPT, etc.) to:
- Draft experiment intakes from natural language
- Validate intakes against the schema
- Route experiments to best-fit labs
- Submit experiments and manage attachments

## Installation

Requires Python 3.10 or newer. The package is not on PyPI yet, so install it from GitHub.

**Run it without installing** (recommended, needs [uv](https://docs.astral.sh/uv/)):

```bash
uvx --from git+https://github.com/litmus-science/litmus-mcp.git litmus-mcp
```

**Or install with pip:**

```bash
pip install "git+https://github.com/litmus-science/litmus-mcp.git"
```

**Or install from source:**

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

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS).

With uv (no install needed):

```json
{
  "mcpServers": {
    "litmus": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/litmus-science/litmus-mcp.git", "litmus-mcp"]
    }
  }
}
```

If you installed with pip:

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

```bash
claude mcp add litmus -- uvx --from git+https://github.com/litmus-science/litmus-mcp.git litmus-mcp
```

Or, if you installed with pip, add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "litmus": {
      "command": "litmus-mcp"
    }
  }
}
```

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
