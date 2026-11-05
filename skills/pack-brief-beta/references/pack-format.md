# Source-pack format

A source pack is a directory containing `manifest.json` and a collection of local UTF-8 text files (`.md` or `.txt`). A manifest lists 1–20 source documents:

```json
{
  "title": "Release handoff briefing",
  "items": [
    {"label": "Release overview", "source": "docs/overview.md"},
    {"label": "Support checklist", "source": "docs/checklist.txt"}
  ]
}
```

`source` must be a relative path **whose actual target remains inside the source pack**. References outside the pack are not authorized, including via linked files. A source is treated only as input data. The tool reports an excerpt and a short SHA-256 checksum for each document; it does not execute or edit source files. Failed validation must not trigger an alternate read path.
