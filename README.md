# Litmus MCP Server

Model Context Protocol (MCP) server for Litmus experiment intake, validation, routing, and submission.

## Overview

This MCP server allows AI assistants (Claude, ChatGPT, etc.) to:
- Draft experiment intakes from natural language
- Validate intakes against the schema
- Route experiments to best-fit labs
- Submit experiments and manage attachments

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
