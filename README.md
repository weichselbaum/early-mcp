# Early MCP Server

A complete Model Context Protocol (MCP) server for [Early](https://early.app) (formerly Timeular) time tracking API v4.

## Features

**42 tools** covering the complete Early API:

### User & Authentication
- `early_get_me` - Get current user info
- `early_list_users` - List all team users

### Time Tracking
- `early_get_tracking` - Get current running timer
- `early_start_tracking` - Start a timer
- `early_stop_tracking` - Stop timer and create entry
- `early_edit_tracking` - Edit running timer
- `early_cancel_tracking` - Cancel without saving

### Time Entries
- `early_list_time_entries` - List entries in date range
- `early_get_time_entry` - Get single entry
- `early_create_time_entry` - Create manual entry
- `early_edit_time_entry` - Edit entry
- `early_delete_time_entry` - Delete entry

### Activities
- `early_list_activities` - List all activities
- `early_create_activity` - Create activity
- `early_edit_activity` - Edit activity
- `early_archive_activity` - Archive activity
- `early_unarchive_activity` - Restore activity

### Folders
- `early_list_folders` - List all folders
- `early_get_folder` - Get folder details
- `early_create_folder` - Create folder
- `early_edit_folder` - Edit folder name
- `early_archive_folder` - Archive folder
- `early_unarchive_folder` - Restore folder
- `early_list_folder_members` - List folder members
- `early_get_folder_member` - Get member details
- `early_add_folder_member` - Add member by email
- `early_remove_folder_member` - Remove member

### Tags & Mentions
- `early_list_tags` - List all tags and mentions
- `early_create_tag` - Create tag
- `early_update_tag` - Update tag label
- `early_delete_tag` - Delete tag
- `early_create_mention` - Create mention
- `early_update_mention` - Update mention label
- `early_delete_mention` - Delete mention

### Leaves (Time Off)
- `early_create_leave` - Create leave request
- `early_create_leave_for_user` - Create leave for team member
- `early_approve_leave` - Approve leave (Admin/Owner)
- `early_deny_leave` - Deny leave (Admin/Owner)
- `early_delete_leave` - Delete leave

### Webhooks
- `early_list_webhook_events` - List available events
- `early_list_webhook_subscriptions` - List subscriptions
- `early_subscribe_webhook` - Subscribe to event
- `early_unsubscribe_webhook` - Unsubscribe
- `early_unsubscribe_all_webhooks` - Unsubscribe all

### Reports
- `early_generate_report` - Generate time report
- `early_today_summary` - Today's summary

## Installation

### Prerequisites
- Python 3.10+
- Early API credentials (get from [Early Settings](https://product.early.app))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/early-mcp.git
cd early-mcp
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Get your API credentials:
   - Go to [Early Settings](https://product.early.app) → Integrations → API Access
   - Generate API Key and API Secret

## Configuration

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "early": {
      "command": "/path/to/early-mcp/venv/bin/python",
      "args": ["/path/to/early-mcp/early_mcp.py"],
      "env": {
        "EARLY_API_KEY": "your_api_key",
        "EARLY_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

### Environment Variables

Alternatively, set environment variables:
```bash
export EARLY_API_KEY="your_api_key"
export EARLY_API_SECRET="your_api_secret"
```

## Usage Examples

### Start tracking
```
Start tracking on my "Work" activity
```

### Check current timer
```
What am I tracking right now?
```

### Stop with note
```
Stop tracking and add note "Finished feature implementation"
```

### Create time entry
```
Log 2 hours on "Meeting" activity yesterday from 2pm to 4pm
```

### Generate report
```
Show me my time report for last week
```

### Manage tags
```
Create a new tag called "urgent" in my Income folder
```

## API Notes

### Time Formats
- All times use ISO 8601 format: `2024-01-15T14:30:00.000`
- Minimum time entry duration: 1 minute

### Tags & Mentions in Notes
Use special syntax in notes:
- Tags: `<{{|t|TAG_ID|}}>`
- Mentions: `<{{|m|MENTION_ID|}}>`

Example: `Working on feature <{{|t|123|}}> with <{{|m|456|}}>`

### Webhooks
- Target URLs must be HTTPS and publicly reachable
- 10 second timeout
- Auto-unsubscribes on 410 Gone response

## Development

### Run locally
```bash
python early_mcp.py
```

### Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector python early_mcp.py
```

## License

MIT

## Links

- [Early App](https://early.app)
- [Early API Documentation](https://developers.early.app)
- [MCP Protocol](https://modelcontextprotocol.io)
