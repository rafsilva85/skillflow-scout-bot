# SkillFlow Skill Scout Bot

[![Available on SkillFlow](https://raw.githubusercontent.com/rafsilva85/awesome-ai-skills/main/badges/skillflow-available.svg)](https://skillflow.builders)

Automated bot that discovers new AI agent skill repositories on GitHub and invites creators to list on [SkillFlow](https://skillflow.builders).

## How It Works

1. Searches GitHub for repos containing `SKILL.md`, `AGENTS.md`, `.cursorrules`, and MCP servers
2. Filters out already-invited repos and own repos
3. Creates a friendly invitation issue in each new repo
4. Runs on a schedule via GitHub Actions (Monday and Thursday)

## Setup

1. Fork this repo
2. The `GITHUB_TOKEN` is automatically provided by GitHub Actions
3. Enable the workflow in your fork's Actions tab

## Manual Run

```bash
GITHUB_TOKEN=your_token python skill_scout.py
```

## Search Queries

The bot searches for:
- `SKILL.md` files in repos
- `AGENTS.md` files in repos
- `.cursorrules` with AI agent skill keywords
- New MCP server repos in TypeScript
- AI agent skill marketplace repos

## Rate Limiting

The bot respects GitHub API rate limits with built-in delays between requests.

## License

MIT
