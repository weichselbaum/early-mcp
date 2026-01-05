# Roadmap

Future features and improvements for Early MCP Server. Contributions and feedback welcome!

## Planned

### Security
- [ ] **Keychain/credential manager support** - Optional secure storage for API keys using system keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service) instead of environment variables

### Usability
- [ ] **Smarter time parsing** - Natural language like "yesterday 2-4pm" or "last Tuesday morning"
- [ ] **Activity fuzzy matching** - Find activities by partial name match instead of exact ID
- [ ] **Default activity** - Set a fallback activity for quick "just start tracking" commands

### Reporting
- [ ] **Weekly digest** - Automated summary with trends, comparisons to previous week
- [ ] **Export formats** - CSV/PDF export for time reports
- [ ] **Billable hours tracking** - Filter and sum by billable flag

### Integrations
- [ ] **Calendar sync** - Cross-reference time entries with calendar events
- [ ] **Pomodoro mode** - Built-in timer with break reminders
- [ ] **Slack status sync** - Update Slack status based on current activity

### Developer Experience
- [ ] **Docker image** - One-line setup without Python environment
- [ ] **Config file support** - YAML/JSON config as alternative to env vars
- [ ] **Verbose/debug mode** - Better logging for troubleshooting

## Ideas (Need Feedback)

These might be useful but need input on priority:

- **Team features** - View team members' current tracking, team reports
- **Goal tracking** - Set weekly hour targets per activity/folder
- **Offline queue** - Buffer commands when API is unreachable
- **Multi-account** - Switch between personal/work Early accounts
- **Activity templates** - Quick-create activities with preset colors/folders

---

**Have an idea?** Open an issue or comment on existing ones!
