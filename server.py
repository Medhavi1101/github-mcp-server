import asyncio
import httpx
import os
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

app = Server("github-mcp-server")


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


# ── Tool 1: List open PRs ─────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_open_prs",
            description="List all open pull requests in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format owner/repo e.g. expressjs/express"
                    }
                },
                "required": ["repo"]
            }
        ),
        types.Tool(
            name="get_pr_diff",
            description="Get the code diff for a specific pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo"},
                    "pr_number": {"type": "integer", "description": "PR number"}
                },
                "required": ["repo", "pr_number"]
            }
        ),
        types.Tool(
            name="get_pr_metadata",
            description="Get title, author, description and status of a pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo"},
                    "pr_number": {"type": "integer", "description": "PR number"}
                },
                "required": ["repo", "pr_number"]
            }
        ),
        types.Tool(
            name="post_pr_comment",
            description="Post a review comment on a pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo"},
                    "pr_number": {"type": "integer", "description": "PR number"},
                    "comment": {"type": "string", "description": "Comment text to post"}
                },
                "required": ["repo", "pr_number", "comment"]
            }
        ),
    ]


# ── Tool implementations ──────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    async with httpx.AsyncClient() as client:

        if name == "list_open_prs":
            repo = arguments["repo"]
            response = await client.get(
                f"{BASE_URL}/repos/{repo}/pulls?state=open",
                headers=get_headers()
            )
            prs = response.json()
            if not prs:
                return [types.TextContent(type="text", text="No open PRs found.")]
            result = "\n".join([
                f"PR #{pr['number']}: {pr['title']} by {pr['user']['login']}"
                for pr in prs[:10]
            ])
            return [types.TextContent(type="text", text=result)]

        elif name == "get_pr_diff":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            response = await client.get(
                f"{BASE_URL}/repos/{repo}/pulls/{pr_number}",
                headers={**get_headers(), "Accept": "application/vnd.github.v3.diff"}
            )
            diff = response.text[:6000]
            return [types.TextContent(type="text", text=diff)]

        elif name == "get_pr_metadata":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            response = await client.get(
                f"{BASE_URL}/repos/{repo}/pulls/{pr_number}",
                headers=get_headers()
            )
            pr = response.json()
            result = f"""Title: {pr['title']}
Author: {pr['user']['login']}
State: {pr['state']}
Created: {pr['created_at']}
Description: {pr.get('body') or 'No description'}
Files changed: {pr.get('changed_files', 'unknown')}
Additions: {pr.get('additions', 0)} | Deletions: {pr.get('deletions', 0)}"""
            return [types.TextContent(type="text", text=result)]

        elif name == "post_pr_comment":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            comment = arguments["comment"]
            response = await client.post(
                f"{BASE_URL}/repos/{repo}/issues/{pr_number}/comments",
                headers=get_headers(),
                json={"body": comment}
            )
            if response.status_code == 201:
                return [types.TextContent(type="text", text="Comment posted successfully.")]
            else:
                return [types.TextContent(type="text", text=f"Failed: {response.text}")]

        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Run the server ────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())