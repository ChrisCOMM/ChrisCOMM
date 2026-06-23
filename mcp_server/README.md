# Local Files MCP Server

A read-only MCP server that lets a local LLM (e.g. via Ollama/llama.cpp with an
MCP-capable client) list and read files from specific folders on your machine.

## Setup

```bash
cd mcp_server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

Specify one or more folders the server is allowed to access:

```bash
python server.py --allowed-dir /home/user/ChrisCOMM/data --allowed-dir /home/user/ChrisCOMM/reports
```

or via environment variable (colon-separated):

```bash
ALLOWED_DIRS="/home/user/ChrisCOMM/data:/home/user/ChrisCOMM/reports" python server.py
```

The server runs over stdio, which is what most MCP clients (Claude Desktop,
Ollama MCP bridges, etc.) expect for locally-spawned servers.

## Tools exposed

- `list_allowed_dirs()` — show which folders are accessible.
- `list_files(path, recursive=False)` — list files/folders under an allowed path.
- `read_file(path, max_bytes=200000)` — read a file's text contents.

Any path outside the allowed folders is rejected.

## Connecting a local Llama client

Most MCP clients use a config entry like:

```json
{
  "mcpServers": {
    "local-files": {
      "command": "/home/user/ChrisCOMM/mcp_server/venv/bin/python",
      "args": [
        "/home/user/ChrisCOMM/mcp_server/server.py",
        "--allowed-dir", "/home/user/ChrisCOMM/data"
      ]
    }
  }
}
```

Check your specific client's docs (e.g. Ollama MCP bridge, LM Studio, or a
custom MCP client you point at your local model) for where this config goes.
