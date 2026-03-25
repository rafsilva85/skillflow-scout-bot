#!/usr/bin/env python3
"""
SkillFlow Skill Scout Bot

Monitors GitHub for new AI agent skill repositories (SKILL.md, AGENTS.md, .cursorrules, etc.)
and creates issues inviting creators to list on SkillFlow.

Designed to run as a GitHub Action on a schedule (daily).

Usage:
    GITHUB_TOKEN=xxx python skill_scout.py
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Search queries to find new skill repos
SEARCH_QUERIES = [
    "SKILL.md in:path created:>{date}",
    "AGENTS.md in:path created:>{date}",
    ".cursorrules in:path ai agent skill created:>{date}",
    "mcp server ai agent created:>{date} language:typescript",
    "ai agent skill marketplace created:>{date}",
    "filename:SKILL.md",
]

# Template for the invitation issue
ISSUE_TITLE = "🎯 List your skill on SkillFlow — the curated marketplace for AI agent skills"

ISSUE_BODY = """Hey there! 👋

I noticed you've built an awesome AI agent skill. Nice work!

I'm building [**SkillFlow**](https://skillflow.builders) — a curated marketplace where developers discover, trust, and install AI agent skills. Think of it as the "npm for AI skills" with trust scores, verified publishers, and cross-platform compatibility.

## Why list on SkillFlow?

- **🔍 Discovery** — Your skill gets found by thousands of AI developers
- **✅ Trust Score** — Verified quality badge for your README
- **📦 Cross-platform** — Works with Claude Code, Cursor, Copilot, Gemini CLI, Manus AI
- **🔌 MCP Integration** — AI agents can discover your skill programmatically via our [MCP Server](https://github.com/rafsilva85/skillflow-mcp-server)
- **📊 Analytics** — Track installs and usage

## How to list

1. Visit [skillflow.builders](https://skillflow.builders)
2. Submit your skill (takes ~2 minutes)
3. Get your SkillFlow badge: [![Available on SkillFlow](https://raw.githubusercontent.com/rafsilva85/awesome-ai-skills/main/badges/skillflow-available.svg)](https://skillflow.builders)

## Quality check

You can validate your skill file before submitting using our [linter](https://github.com/rafsilva85/skillflow-linter):

```bash
python skillflow_linter.py SKILL.md
```

---

*This is an automated invitation from the SkillFlow Scout Bot. If you're not interested, feel free to close this issue. No hard feelings!*

— [SkillFlow](https://skillflow.builders) | [Awesome AI Skills](https://github.com/rafsilva85/awesome-ai-skills)
"""

def search_repos(query, date_str):
    """Search GitHub for repos matching the query."""
    q = query.replace("{date}", date_str)
    url = f"https://api.github.com/search/repositories?q={requests.utils.quote(q)}&sort=created&order=desc&per_page=10"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json().get("items", [])
        else:
            print(f"  Search error: {r.status_code}")
            return []
    except Exception as e:
        print(f"  Search exception: {e}")
        return []

def search_code(query, date_str):
    """Search GitHub code for files matching the query."""
    q = query.replace("{date}", date_str)
    url = f"https://api.github.com/search/code?q={requests.utils.quote(q)}&sort=indexed&order=desc&per_page=10"
    try:
        r = requests.get(url, headers={**HEADERS, "Accept": "application/vnd.github.v3.text-match+json"}, timeout=15)
        if r.status_code == 200:
            return r.json().get("items", [])
        return []
    except:
        return []

def has_existing_issue(owner, repo):
    """Check if we already created an issue in this repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?creator=rafsilva85&state=all&per_page=5"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            for issue in r.json():
                if "SkillFlow" in issue.get("title", ""):
                    return True
        return False
    except:
        return False

def create_issue(owner, repo):
    """Create an invitation issue in the repo."""
    if owner == "rafsilva85":
        print(f"  Skipping own repo: {owner}/{repo}")
        return False
    
    if has_existing_issue(owner, repo):
        print(f"  Already invited: {owner}/{repo}")
        return False
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    r = requests.post(url, headers=HEADERS, json={
        "title": ISSUE_TITLE,
        "body": ISSUE_BODY,
        "labels": ["enhancement"]
    }, timeout=15)
    
    if r.status_code == 201:
        print(f"  ✅ Issue created: {owner}/{repo}")
        return True
    else:
        print(f"  ❌ Issue failed ({r.status_code}): {owner}/{repo}")
        return False

def main():
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN not set")
        return
    
    date_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"🔍 SkillFlow Skill Scout — Searching repos since {date_str}")
    
    seen_repos = set()
    invited = 0
    
    for query in SEARCH_QUERIES:
        print(f"\n  Query: {query.replace('{date}', date_str)[:60]}...")
        
        if "in:path" in query or "filename:" in query:
            items = search_code(query, date_str)
            for item in items:
                repo = item.get("repository", {})
                full_name = repo.get("full_name", "")
                if full_name and full_name not in seen_repos:
                    seen_repos.add(full_name)
                    owner, name = full_name.split("/")
                    if create_issue(owner, name):
                        invited += 1
                    time.sleep(2)  # Rate limiting
        else:
            items = search_repos(query, date_str)
            for item in items:
                full_name = item.get("full_name", "")
                if full_name and full_name not in seen_repos:
                    seen_repos.add(full_name)
                    owner, name = full_name.split("/")
                    if create_issue(owner, name):
                        invited += 1
                    time.sleep(2)
        
        time.sleep(5)  # Rate limiting between queries
    
    print(f"\n📊 Results: {len(seen_repos)} repos found, {invited} invitations sent")
    
    # Save results
    with open("scout_results.json", "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "repos_found": len(seen_repos),
            "invitations_sent": invited,
            "repos": list(seen_repos)
        }, f, indent=2)

if __name__ == "__main__":
    main()
