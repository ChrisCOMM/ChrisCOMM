# Local Files MCP Server

A read-only MCP server that lets a local LLM (e.g. via Ollama/llama.cpp with an
MCP-capable client) list and read files from specific folders on your machine.

## Setup

Requires [`uv`](https://docs.astral.sh/uv/).

```bash
cd mcp_server
uv sync
```

## Run

By default the server only allows access to:

```
C:\Users\EU01242390\Investigations\Case_FIles
```

Just run it with no arguments to use that folder:

```bash
uv run server.py
```

To point it at a different folder instead, pass `--allowed-dir` (repeatable)
or set the `ALLOWED_DIRS` env var (colon-separated paths):

```bash
uv run server.py --allowed-dir C:\some\other\folder

ALLOWED_DIRS="/home/user/ChrisCOMM/data:/home/user/ChrisCOMM/reports" uv run server.py
```

By default the server runs over stdio, which is what clients that spawn it
themselves expect (Claude Desktop, Ollama MCP bridges, etc.).

Browser-based GUIs that connect to an MCP server by URL instead — like
**llama.cpp's built-in web UI** — need the `sse` (or `streamable-http`)
transport instead. Run the server as a standalone process:

```bash
uv run server.py --transport sse --host 127.0.0.1 --port 8765
```

Then in llama.cpp GUI's settings, add an MCP server pointing at:

```
http://127.0.0.1:8765/sse
```

(If your version of llama.cpp's GUI expects `streamable-http` instead of
`sse`, use `--transport streamable-http` and the URL it asks for — check
the exact path your version expects.)

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
      "command": "uv",
      "args": [
        "run",
        "--directory", "/home/user/ChrisCOMM/mcp_server",
        "server.py"
      ]
    }
  }
}
```

Check your specific client's docs (e.g. Ollama MCP bridge, LM Studio, or a
custom MCP client you point at your local model) for where this config goes.
