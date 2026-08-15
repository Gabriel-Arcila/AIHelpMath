---
name: notion-md-to-page
description: Converts Markdown files into Notion pages within any database, using the Notion MCP server. Handles the full pipeline from .md parsing to block insertion with proper chunking. Use this skill whenever the user wants to upload, export, migrate, or convert a .md file to Notion, create a Notion page from documentation, notes, changelogs, or any Markdown content, or insert structured Markdown (with tables, code blocks, callouts, task lists, frontmatter) into a Notion database. Do NOT use for editing existing Notion pages, reading from Notion, or non-Markdown sources.
---

## Use this skill when

- You need to create a Notion page from a Markdown (`.md`) file
- You need to insert the content of a `.md` document into an existing Notion database
- You need to convert Markdown content into Notion API block format
- You need to migrate documentation files to Notion

## Do not use this skill when

- You need to edit an existing Notion page (use `API-patch-page` or `API-update-a-block` directly)
- The content source is not Markdown
- You need to work with Notion pages that are NOT inside a database

## Prerequisites

- The `notion-mcp-server` MCP server must be connected and available
- Node.js must be installed on the system (for the parser script)
- You must know the **database_id** of the target Notion database, OR the exact name to search for it

---

## Instructions

Follow these steps **in order** to insert a Markdown document into any Notion database.

### Step 1 — Identify the Target Database

If you already have the `database_id`, skip to Step 2.

**Search for the database by name:**

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-post-search
```

```json
{
  "query": "<DATABASE NAME>",
  "filter": {
    "property": "object",
    "value": "data_source"
  }
}
```

Look for `"object": "database"` in the results and extract its `id`.

**Verify the schema (recommended):**

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-retrieve-a-database
```

```json
{
  "database_id": "<DATABASE_ID>"
}
```

This returns all properties and their types. **Record the following:**
- The **title property name** (the property with `"type": "title"`) — you need this for Step 2
- All other property names and types (status, select, multi_select, etc.) — for optional metadata

---

### Step 2 — Create the Page (Entry in the Database)

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-post-page
```

**Minimal arguments (title only):**

```json
{
  "parent": {
    "database_id": "<DATABASE_ID>",
    "type": "database_id"
  },
  "properties": {
    "<TITLE_PROPERTY_NAME>": {
      "title": [
        {
          "text": {
            "content": "<document-name.md>"
          }
        }
      ]
    }
  }
}
```

**With optional properties** (adapt property names/types to YOUR database schema):

```json
{
  "parent": {
    "database_id": "<DATABASE_ID>",
    "type": "database_id"
  },
  "properties": {
    "<TITLE_PROPERTY_NAME>": {
      "title": [{ "text": { "content": "<document-name.md>" } }]
    },
    "<STATUS_PROPERTY>": {
      "status": { "name": "<status-value>" }
    },
    "<SELECT_PROPERTY>": {
      "select": { "name": "<option-value>" }
    },
    "<MULTI_SELECT_PROPERTY>": {
      "multi_select": [{ "name": "<option-value>" }]
    }
  }
}
```

> **⚠️ CRITICAL**: Save the `id` from the response — this is your `PAGE_ID` needed for Step 4.

> **⚠️ IMPORTANT**: The `children` field in `API-post-page` accepts an array of **strings**, NOT block objects. To insert structured content (headings, code blocks, tables, etc.), you MUST use `API-patch-block-children` in Step 4.

#### Property type reference for common schemas

| Property Type    | JSON Structure                                              |
|------------------|-------------------------------------------------------------|
| `title`          | `{ "title": [{ "text": { "content": "..." } }] }`          |
| `rich_text`      | `{ "rich_text": [{ "text": { "content": "..." } }] }`      |
| `status`         | `{ "status": { "name": "..." } }`                           |
| `select`         | `{ "select": { "name": "..." } }`                           |
| `multi_select`   | `{ "multi_select": [{ "name": "..." }] }`                   |
| `number`         | `{ "number": 42 }`                                           |
| `checkbox`       | `{ "checkbox": true }`                                       |
| `url`            | `{ "url": "https://..." }`                                   |
| `email`          | `{ "email": "user@example.com" }`                            |
| `date`           | `{ "date": { "start": "2026-01-01" } }`                     |

---

### Step 3 — Convert Markdown to Notion Block JSON

Use the parser script included with this skill to convert the `.md` file:

```bash
node <SKILL_DIR>/scripts/md-to-notion.js "<path/to/file.md>" "<output-directory>"
```

This will create one or more `chunk_N.json` files in the output directory. Each chunk contains ≤100 blocks (the Notion API limit per call).

**Example:**
```bash
node .agents/skills/notion-md-to-page/scripts/md-to-notion.js "spec/my-document.md" "spec/notion-output"
```

Output:
```
✅ Done — 247 blocks → 3 chunk(s) written to spec/notion-output
```

#### Parser features

- **YAML frontmatter detection**: Files starting with `---` (YAML frontmatter) are automatically detected and skipped. The frontmatter is NOT converted into Notion blocks.
- **Language validation**: Code fence languages are validated against Notion's supported language set. Unknown languages fall back to `plain text`. Common aliases (`js` → `javascript`, `py` → `python`, `ts` → `typescript`, etc.) are resolved automatically.
- **Auto-splitting**: Text exceeding 2000 characters per `rich_text` segment is automatically split.

#### What the parser converts

| Markdown Element            | Notion Block Type        | Notes                                    |
|-----------------------------|--------------------------|------------------------------------------|
| `# Heading`                 | `heading_1`              |                                          |
| `## Heading`                | `heading_2`              |                                          |
| `### Heading`               | `heading_3`              |                                          |
| `#### Heading` (4+)         | `heading_3`              | Notion only supports 3 levels            |
| Plain text                  | `paragraph`              |                                          |
| `**bold**`                  | `annotations.bold`       | Inside `rich_text`                       |
| `*italic*`                  | `annotations.italic`     | Inside `rich_text`                       |
| `` `code` ``                | `annotations.code`       | Inside `rich_text`                       |
| `~~strikethrough~~`         | `annotations.strikethrough` | Inside `rich_text`                    |
| `[text](url)`               | `text.link`              | Inside `rich_text` with `link.url`       |
| `- item` / `* item`         | `bulleted_list_item`     | Each item = separate block               |
| `1. item`                   | `numbered_list_item`     | Each item = separate block               |
| `- [x] task` / `- [ ] task` | `to_do`                  | With `checked: true/false`               |
| ` ```lang ... ``` `         | `code`                   | With validated `language`                |
| `> quote`                   | `quote`                  |                                          |
| `---`                       | `divider`                |                                          |
| `> [!WARNING]` etc.         | `callout`                | With appropriate emoji icon              |
| `| table |`                 | `table` + `table_row`    | Requires `children` with rows            |

#### GitHub Alert → Callout emoji mapping

| Alert Type      | Emoji |
|-----------------|-------|
| `[!NOTE]`       | ℹ️    |
| `[!TIP]`        | 💡    |
| `[!IMPORTANT]`  | ❗    |
| `[!WARNING]`    | ⚠️    |
| `[!CAUTION]`    | 🔴    |

#### Parser input/output example

**Markdown input:**

```markdown
# My Document

This is a **bold** word and an *italic* word.

> [!TIP]
> This is a helpful tip.

- Item one
- Item two
```

**JSON output (single chunk):**

```json
[
  {
    "type": "heading_1",
    "heading_1": {
      "rich_text": [{ "type": "text", "text": { "content": "My Document" } }]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [
        { "type": "text", "text": { "content": "This is a " } },
        { "type": "text", "text": { "content": "bold" }, "annotations": { "bold": true } },
        { "type": "text", "text": { "content": " word and an " } },
        { "type": "text", "text": { "content": "italic" }, "annotations": { "italic": true } },
        { "type": "text", "text": { "content": " word." } }
      ]
    }
  },
  {
    "type": "callout",
    "callout": {
      "rich_text": [{ "type": "text", "text": { "content": "This is a helpful tip." } }],
      "icon": { "type": "emoji", "emoji": "💡" }
    }
  },
  {
    "type": "bulleted_list_item",
    "bulleted_list_item": {
      "rich_text": [{ "type": "text", "text": { "content": "Item one" } }]
    }
  },
  {
    "type": "bulleted_list_item",
    "bulleted_list_item": {
      "rich_text": [{ "type": "text", "text": { "content": "Item two" } }]
    }
  }
]
```

#### Parser limitations

- No nested list support (items are flattened to a single level)
- No image support (local images cannot be uploaded via the API)
- No HTML tag parsing (HTML is treated as plain text)
- No footnotes or anchor link support
- No combined formatting (`***bold italic***` is not parsed as both)
- Maximum 2000 characters per `rich_text` segment (auto-split by the parser)

---

### Step 4 — Insert Content into the Page (Auto-Upload)

> **⚠️ IMPORTANT LIMITATION:** Because `chunk_N.json` files can be extremely large (up to 70+ KB) and exceed LLM output token limits, you MUST NOT try to manually pass their contents to `API-patch-block-children` via `call_mcp_tool`.

Instead, use the included `push_chunks.js` script to directly upload all chunks and automatically fix any invalid local URLs.

```bash
node <SKILL_DIR>/scripts/push_chunks.js "<PAGE_ID>" "<output-directory>"
```

**Example:**
```bash
node .agents/skills/notion-md-to-page/scripts/push_chunks.js "3886caf8-da64-8144-967f-f09010aba983" "spec/notion-output"
```

The script will automatically:
1. Extract the Notion API token from your MCP configuration (`~/.gemini/config/mcp_config.json`).
2. Read the JSON chunks in order.
3. Automatically fix invalid local URLs (replacing them with placeholders to prevent Notion validation errors).
4. Subdivide blocks further if necessary and upload them respecting rate limits.
5. Clean up the output directory automatically.

---

### Step 5 — Verify Clean Up

Although `push_chunks.js` automatically attempts to delete the chunk files and the output directory upon successful upload, you should verify that the temporary files were removed to avoid leaving artifacts in the project:

```bash
# Verify the output directory no longer exists
ls "<output-directory>"
```

If the directory still exists, remove it manually:

```bash
rm -rf "<output-directory>"
```

Or on Windows:
```powershell
Remove-Item -Path "<output-directory>" -Recurse -Force
```

---

### Step 6 — Update Page Properties (Optional)

After inserting content, you can update the page status or other properties:

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-patch-page
```

```json
{
  "page_id": "<PAGE_ID>",
  "properties": {
    "<STATUS_PROPERTY>": {
      "status": { "name": "<new-status>" }
    }
  }
}
```

**To add a page icon:**

```json
{
  "page_id": "<PAGE_ID>",
  "icon": { "emoji": "📄" }
}
```

---

### Step 7 — Verify the Insertion

**Check that the page exists in the database:**

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-query-data-source
```

```json
{
  "data_source_id": "<DATABASE_ID>",
  "filter": {
    "property": "<TITLE_PROPERTY_NAME>",
    "title": {
      "equals": "<document-name.md>"
    }
  }
}
```

**Check the page content:**

```
Tool:   call_mcp_tool
Server: notion-mcp-server
Tool:   API-get-block-children
```

```json
{
  "block_id": "<PAGE_ID>"
}
```

Verify that the block count and structure match what you expected.

---

## Complete Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│               MARKDOWN → NOTION PAGE FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Identify target database (API-post-search or known ID)      │
│           │                                                     │
│           ▼                                                     │
│  2. Retrieve schema (API-retrieve-a-database)                   │
│           │  → Note title property name + other properties      │
│           ▼                                                     │
│  3. Create page entry (API-post-page)                           │
│           │  → Save the returned PAGE_ID                        │
│           ▼                                                     │
│  4. Convert .md → JSON chunks (node md-to-notion.js)            │
│           │  → Generates chunk_0.json, chunk_1.json, ...        │
│           ▼                                                     │
│  5. Upload chunks automatically (node push_chunks.js)           │
│           │  → Fixes links, uploads, and auto-cleans directory  │
│           ▼                                                     │
│  6. Verify Clean Up (check and delete output directory)         │
│           │                                                     │
│           ▼                                                     │
│  7. Update properties (API-patch-page) [optional]               │
│           │                                                     │
│           ▼                                                     │
│  8. Verify (API-get-block-children)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Limits Reference

| Limit                               | Value                              |
|--------------------------------------|-------------------------------------|
| Blocks per `patch-block-children`    | **100 maximum**                    |
| Characters per `rich_text` object    | **2000 maximum**                   |
| `rich_text` objects per block        | **100 maximum**                    |
| Rate limit                           | **3 requests/second** per integration |
| Nesting depth                        | **~3 levels**                      |

## Block Types Reference

| Block Type               | In MCP Schema | Notes                              |
|--------------------------|---------------|-------------------------------------|
| `paragraph`              | ✅ Formal     |                                    |
| `bulleted_list_item`     | ✅ Formal     |                                    |
| `heading_1` / `2` / `3`  | ⚡ Runtime    | Works at runtime, not in schema    |
| `numbered_list_item`     | ⚡ Runtime    | Works at runtime, not in schema    |
| `code`                   | ⚡ Runtime    | Works at runtime, not in schema    |
| `quote`                  | ⚡ Runtime    | Works at runtime, not in schema    |
| `to_do`                  | ⚡ Runtime    | Works at runtime, not in schema    |
| `divider`                | ⚡ Runtime    | Works at runtime, not in schema    |
| `callout`                | ⚡ Runtime    | Works at runtime, not in schema    |
| `table` + `table_row`   | ⚡ Runtime    | Works at runtime, not in schema    |

> **Runtime** types are not defined in the MCP formal schema but are accepted by the Notion API. Pass them as valid JSON block objects.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `"validation_error"` on page creation | Wrong property name or type | Run `API-retrieve-a-database` to verify the exact property names and types |
| Content not appearing | Used `children` in `API-post-page` with block objects | Use `API-patch-block-children` after creating the page |
| Truncated code blocks | Code exceeded 2000 chars | The parser auto-splits; verify the chunks are correct |
| `"rate_limited"` errors | Too many rapid API calls | Add delays between chunk insertions |
| Table not rendering | Missing separator row handling | The parser skips `\|---\|` rows automatically |
| YAML frontmatter as dividers | Parser treating `---` as horizontal rule | Already fixed: frontmatter is auto-detected and skipped |
| Unknown code language | Language not recognized by Notion | Parser auto-resolves aliases and falls back to `plain text` |

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- The parser script uses regex-based parsing — deeply nested or complex Markdown may need manual adjustments.
- Images cannot be uploaded through the Notion API; use external URLs instead.
- Stop and ask for clarification if the database schema is unknown or unclear.
