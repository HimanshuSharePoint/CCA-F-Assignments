"""NorthPeak policy-documents MCP server.

Exposes three tools over STDIO:

1. list_docs()
   Returns the names of all available policy documents.

2. read_doc(name)
   Returns the complete text of one policy document.

3. search_docs(query)
   Searches all policy documents and returns matching snippets.

The policy documents are loaded from data/docs/.
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP


# Create the MCP server.
mcp = FastMCP("northpeak-docs")


# Build an absolute path to the policy-document folder.
# This allows the server to work regardless of the current folder.
DOCS_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "docs"
)


def _doc_paths() -> list:
    """Return all Markdown policy-document paths alphabetically."""

    return sorted(DOCS_DIR.glob("*.md"))


@mcp.tool()
def list_docs() -> list:
    """Return available policy-document names without .md extensions."""

    return [path.stem for path in _doc_paths()]


@mcp.tool()
def read_doc(name: str) -> str:
    """Return the complete text of one policy document.

    The document name may be supplied with or without the .md extension.
    For example: returns-policy or returns-policy.md.
    """

    stem = name[:-3] if name.endswith(".md") else name
    document_path = DOCS_DIR / f"{stem}.md"

    if not document_path.exists():
        available_docs = ", ".join(
            path.stem for path in _doc_paths()
        )

        return (
            f"No document named {stem!r}. "
            f"Available documents: {available_docs}."
        )

    return document_path.read_text(encoding="utf-8")


@mcp.tool()
def search_docs(query: str) -> list:
    """Search policy documents using case-insensitive text matching.

    Each matching result contains the document name and a short snippet
    around the first occurrence of the search query.
    """

    normalized_query = query.strip().lower()
    results = []

    if not normalized_query:
        return results

    for document_path in _doc_paths():
        document_text = document_path.read_text(encoding="utf-8")
        match_index = document_text.lower().find(normalized_query)

        if match_index == -1:
            continue

        snippet_start = max(0, match_index - 40)
        snippet_end = min(
            len(document_text),
            match_index + len(normalized_query) + 40,
        )

        snippet = (
            document_text[snippet_start:snippet_end]
            .replace("\n", " ")
            .strip()
        )

        results.append(
            {
                "name": document_path.stem,
                "snippet": f"...{snippet}...",
            }
        )

    return results


if __name__ == "__main__":
    # Start the MCP server using STDIO transport.
    mcp.run()
