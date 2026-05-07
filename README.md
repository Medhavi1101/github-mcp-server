# GitHub MCP Server

A custom Model Context Protocol (MCP) server that connects Claude Desktop directly to GitHub. Claude autonomously decides which tools to call based on a plain English goal — no manual orchestration needed.

---

## What it does

Instead of you telling Claude *how* to fetch data, you give Claude a *goal* and it figures out which tools to call, in what order, and how many times.

**Example:**
> You type: *"Review all open PRs in expressjs/express and flag any that touch auth code"*

Claude autonomously:
1. Calls `list_open_prs` → gets 10 PRs
2. Calls `get_pr_diff` on each one
3. Calls `get_pr_metadata` to check which files changed
4. Calls `post_pr_comment` on the ones that touch auth

You didn't write a single line of orchestration code.

---

## Tools exposed

| Tool | Description |
|---|---|
| `list_open_prs` | List all open pull requests in a repository |
| `get_pr_diff` | Fetch the full code diff for a specific PR |
| `get_pr_metadata` | Get title, author, description, files changed |
| `post_pr_comment` | Post a review comment on a PR |

---

## Tech stack

| Layer | Technology |
|---|---|
| Protocol | Model Context Protocol (MCP) |
| Runtime | Python 3.12 |
| GitHub integration | GitHub REST API v3 |
| Transport | stdio (standard MCP transport) |
| Client | Claude Desktop |

---

## CCA exam domains covered

| Domain | Weight | How this project covers it |
|---|---|---|
| Tool Design & MCP Integration | 18% | Full MCP server with 4 production-ready tools |
| Agentic Architecture & Orchestration | 27% | Claude autonomously orchestrates multi-step GitHub workflows |
| Claude Code Configuration & Workflows | 20% | MCP server config, stdio transport, tool schema design |

---

## Project structure

```
github-mcp-server/
├── server.py      # MCP server with all 4 tools
├── .env.example   # Environment variable template
└── requirements.txt
```

---

## Setup

### 1. Requirements

- Python 3.10+ (3.12 recommended)
- Claude Desktop installed (`claude.ai/download`)
- GitHub personal access token

### 2. Clone and install

```bash
git clone https://github.com/Medhavi1101/github-mcp-server
cd github-mcp-server
python3.12 -m venv venv
source venv/bin/activate
pip install "mcp[cli]" httpx python-dotenv
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
GITHUB_TOKEN=ghp_your-token-here
```

### 4. Connect to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "/path/to/your/venv/bin/python3",
      "args": ["/path/to/github-mcp-server/server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your-token-here"
      }
    }
  }
}
```

Restart Claude Desktop. You'll see the tools available in the chat.

### 5. Test it

In Claude Desktop, type:
```
List open PRs in expressjs/express
```

Claude will call your `list_open_prs` tool automatically and return live results.

---

## How MCP differs from a regular API

| Regular API | MCP Server |
|---|---|
| You call the API | Claude calls the tools |
| You write orchestration logic | Claude decides the order |
| Fixed workflow | Dynamic, goal-driven |
| You handle errors and retries | Claude adapts autonomously |

---

## Related project

This MCP server pairs with the [AI Code Reviewer API](https://github.com/Medhavi1101/ai-code-reviewer) — a FastAPI backend that uses Claude tool use to return structured code reviews. Together they form a complete agentic code review system.

---

## Author

Medhavi Math — Backend Developer transitioning into AI Engineering
- Studying for Claude Certified Architect (CCA) exam
- [LinkedIn](https://linkedin.com/in/your-profile)
