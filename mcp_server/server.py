"""
Read-only MCP server exposing files under a configured set of local folders.

Allowed folders are set via the ALLOWED_DIRS environment variable
(colon-separated absolute paths) or the --allowed-dir CLI flag (repeatable).
Only paths that resolve inside one of these folders can be listed or read.
"""
import argparse
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("local-files")

DEFAULT_ALLOWED_DIR = r"C:\Users\EU01242390\Investigations\Case_FIles"

ALLOWED_DIRS: list[Path] = []


def _resolve_allowed(path_str: str) -> Path:
    candidate = Path(path_str).expanduser().resolve()
    for allowed in ALLOWED_DIRS:
        if candidate == allowed or allowed in candidate.parents:
            return candidate
    raise ValueError(f"Path {path_str!r} is outside the allowed directories")


@mcp.tool()
def list_allowed_dirs() -> list[str]:
    """List the local folders this server is permitted to read from."""
    return [str(p) for p in ALLOWED_DIRS]


@mcp.tool()
def list_files(path: str, recursive: bool = False) -> list[str]:
    """List files and subfolders under an allowed folder.

    Args:
        path: Absolute path of an allowed folder or a subfolder within it.
        recursive: If true, list all files in subfolders too.
    """
    target = _resolve_allowed(path)
    if not target.is_dir():
        raise ValueError(f"{path!r} is not a directory")
    pattern = "**/*" if recursive else "*"
    return sorted(str(p) for p in target.glob(pattern))


@mcp.tool()
def read_file(path: str, max_bytes: int = 200_000) -> str:
    """Read the text contents of a file within an allowed folder.

    Args:
        path: Absolute path of the file to read.
        max_bytes: Maximum number of bytes to read (default 200,000).
    """
    target = _resolve_allowed(path)
    if not target.is_file():
        raise ValueError(f"{path!r} is not a file")
    with open(target, "r", encoding="utf-8", errors="replace") as f:
        return f.read(max_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allowed-dir",
        action="append",
        default=[],
        help="Folder to allow access to (repeatable)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport to serve over. Use 'sse' or 'streamable-http' for "
        "browser-based clients (e.g. llama.cpp's GUI) that connect via a URL "
        "instead of spawning this script as a subprocess.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to when using the sse/streamable-http transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind to when using the sse/streamable-http transport.",
    )
    args = parser.parse_args()

    dirs = list(args.allowed_dir)
    env_dirs = os.environ.get("ALLOWED_DIRS", "")
    if env_dirs:
        dirs.extend(env_dirs.split(":"))

    if not dirs:
        dirs = [DEFAULT_ALLOWED_DIR]

    for d in dirs:
        resolved = Path(d).expanduser().resolve()
        if not resolved.is_dir():
            parser.error(f"{d!r} is not a directory")
        ALLOWED_DIRS.append(resolved)

    if args.transport != "stdio":
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
