# Early MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A complete [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for [Early](https://early.app) (formerly Timeular) time tracking API v4.

Use natural language to track time, manage activities, generate reports, and more—directly from Claude.

## Quick Start

### 1. Get API Credentials

1. Go to [Early Account Settings](https://product.early.app/#/settings/account)
2. Scroll to the bottom to find the **API** section
3. Generate your API Key and API Secret

### 2. Install

```bash
git clone https://github.com/weichselbaum/early-mcp.git
cd early-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "early": {
      "command": "/absolute/path/to/early-mcp/venv/bin/python",
      "args": ["/absolute/path/to/early-mcp/early_mcp.py"],
      "env": {
        "EARLY_API_KEY": "your_api_key_here",
        "EARLY_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

The Early tools should now appear in Claude.

## Usage Examples

**Start tracking:**
> "Start tracking on LWX"

**Check current timer:**
> "What am I working on?"

**Stop with note:**
> "Stop tracking, note: finished feature implementation"

**Log time manually:**
> "Log 2 hours on Meeting yesterday from 2pm to 4pm"

**Weekly report:**
> "Show me my time report for last week"

**Team report (per-user breakdown):**
> "Generate a report for the whole team for May, broken down by member"

**Find odd patterns:**
> "Analyze our time distribution for Q2 and flag anyone booking unusually high time on Organisation compared to the team"

**Manage tags:**
> "Create a tag called 'urgent' in my Income folder"

## Features

**48 tools** covering the complete Early API:

| Category | Tools | Description |
|----------|-------|-------------|
| **User** | 2 | Get current user, list team users |
| **Tracking** | 5 | Start, stop, edit, cancel, get current |
| **Time Entries** | 5 | List, get, create, edit, delete |
| **Activities** | 5 | List, create, edit, archive, unarchive |
| **Folders** | 10 | Full CRUD + member management |
| **Tags** | 4 | List, create, update, delete |
| **Mentions** | 3 | Create, update, delete |
| **Leaves** | 5 | Create, approve, deny, delete |
| **Webhooks** | 5 | List events, subscribe, unsubscribe |
| **Reports** | 4 | Generate report (with per-user breakdown), analyze time distribution, export raw entries for range, today summary |

## API Notes

### Time Formats
All times use ISO 8601: `2024-01-15T14:30:00.000`

Time entry timestamps are **UTC** (no offset suffix). Report-based tools (`early_generate_report`, `early_analyze_time_distribution`, `early_export_raw_entries_for_range`) return a per-entry `timezone` (e.g. `Europe/Berlin`, or `Z` for UTC) - convert UTC to that zone before reasoning about time-of-day or weekday/weekend. The personal `early_list_time_entries` endpoint returns no per-entry timezone.

### Minimum Duration
Time entries require at least 1 minute duration.

### Tags & Mentions in Notes
Special syntax for notes:
- Tags: `<{{|t|TAG_ID|}}>`
- Mentions: `<{{|m|MENTION_ID|}}>`

### Personal vs. Team Scope
- `early_list_time_entries` is **personal-scope**: it returns only the authenticated account's individual entries and does not accept a user filter.
- For team-wide data use `early_generate_report` (aggregated, optional `user_ids`, per-user breakdown when multiple members are present), `early_analyze_time_distribution` (per-user x activity matrix with team baselines), or `early_export_raw_entries_for_range` (raw individual entries grouped per user, for fine-grained pattern analysis).
- Seeing other members' entries requires **Full access** to their folder. Omit `user_ids` to include every member you have Full access to.

## Development

```bash
# Run locally
python early_mcp.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python early_mcp.py
```

## License

MIT - see [LICENSE](LICENSE)

## API Documentation

The `docs/` folder contains reference documentation for developers who want to understand the Early API or build custom implementations:

- **EARLY_API_V4_REFERENCE.md** - Markdown reference covering all endpoints, parameters, and response formats
- **early_api_v4_collection.json** - Full Postman collection export

### How the docs were sourced

The JSON collection was exported from [Early's official Postman workspace](https://developers.early.app). Click "Run in Postman" (top right), fork the collection to your own workspace, then export as JSON. The collection is maintained by Timeular (Early's parent company).

## Links

- [Early App](https://early.app)
- [Early API Docs](https://developers.early.app)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/download)

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and ideas. Feedback welcome!
