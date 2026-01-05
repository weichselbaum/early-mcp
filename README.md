# Early MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A complete [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for [Early](https://early.app) (formerly Timeular) time tracking API v4.

Use natural language to track time, manage activities, generate reports, and more—directly from Claude.

## Quick Start

### 1. Get API Credentials

1. Go to [Early App](https://product.early.app) → Settings → Integrations → API Access
2. Generate your API Key and API Secret

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

**Manage tags:**
> "Create a tag called 'urgent' in my Income folder"

## Features

**46 tools** covering the complete Early API:

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
| **Reports** | 2 | Generate report, today summary |

## API Notes

### Time Formats
All times use ISO 8601: `2024-01-15T14:30:00.000`

### Minimum Duration
Time entries require at least 1 minute duration.

### Tags & Mentions in Notes
Special syntax for notes:
- Tags: `<{{|t|TAG_ID|}}>`
- Mentions: `<{{|m|MENTION_ID|}}>`

## Development

```bash
# Run locally
python early_mcp.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python early_mcp.py
```

## License

MIT - see [LICENSE](LICENSE)

## Links

- [Early App](https://early.app)
- [Early API Docs](https://developers.early.app)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/download)
