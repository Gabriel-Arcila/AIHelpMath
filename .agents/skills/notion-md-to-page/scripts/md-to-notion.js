/**
 * md-to-notion.js — Markdown to Notion Block JSON Converter
 *
 * Converts a Markdown (.md) file into Notion API-compatible
 * block JSON, split into chunks of ≤100 blocks each
 * (Notion API limit per call).
 *
 * Usage:
 *   node md-to-notion.js <input.md> <output-directory>
 *
 * Output:
 *   <output-directory>/chunk_0.json
 *   <output-directory>/chunk_1.json
 *   ...
 *
 * Supported Markdown elements:
 *   - Headings (#, ##, ###, ####+)
 *   - Paragraphs
 *   - Bold (**text**), Italic (*text*), Inline code (`text`)
 *   - Strikethrough (~~text~~)
 *   - Links [text](url)
 *   - Bulleted lists (- item, * item)
 *   - Numbered lists (1. item)
 *   - Task lists (- [x] done, - [ ] todo)
 *   - Code blocks (```lang ... ```)
 *   - Blockquotes (> text)
 *   - GitHub-style alerts (> [!NOTE], > [!WARNING], etc.)
 *   - Horizontal rules (---)
 *   - Tables (| col | col |)
 *
 * Limitations:
 *   - No nested list support (items are flattened)
 *   - No image support (local images can't be uploaded)
 *   - No HTML tag parsing
 *   - No footnotes or anchor links
 */

const fs = require('fs');
const path = require('path');

// ── CLI Arguments ──────────────────────────────────────────────
const inputFile = process.argv[2];
const outputDir = process.argv[3];

if (!inputFile || !outputDir) {
    console.error(
        'Usage: node md-to-notion.js <input.md> <output-directory>'
    );
    process.exit(1);
}

if (!fs.existsSync(inputFile)) {
    console.error(`Error: Input file not found: ${inputFile}`);
    process.exit(1);
}

if (!inputFile.toLowerCase().endsWith('.md')) {
    console.warn(
        `Warning: Input file "${inputFile}" does not have .md extension`
    );
}

// ── Constants ──────────────────────────────────────────────────
const MAX_RICH_TEXT_LENGTH = 2000;
const CHUNK_SIZE = 100;

// ── Notion Supported Languages ─────────────────────────────────
const NOTION_LANGUAGES = new Set([
    'abap', 'arduino', 'bash', 'basic', 'c', 'clojure',
    'coffeescript', 'cpp', 'csharp', 'css', 'dart', 'diff',
    'docker', 'elixir', 'elm', 'erlang', 'flow', 'fortran',
    'fsharp', 'gherkin', 'glsl', 'go', 'graphql', 'groovy',
    'haskell', 'html', 'java', 'javascript', 'json', 'julia',
    'kotlin', 'latex', 'less', 'lisp', 'livescript', 'lua',
    'makefile', 'markdown', 'markup', 'matlab', 'mermaid',
    'nix', 'objective-c', 'objectivec', 'ocaml', 'pascal',
    'perl', 'php', 'plain text', 'powershell', 'prolog',
    'protobuf', 'python', 'r', 'reason', 'ruby', 'rust',
    'sass', 'scala', 'scheme', 'scss', 'shell', 'sql',
    'swift', 'toml', 'typescript', 'vb.net', 'vbnet',
    'verilog', 'vhdl', 'visual basic', 'webassembly', 'xml',
    'yaml', 'java/c/c++/c#',
]);

// ── Language Aliases ───────────────────────────────────────────
const LANGUAGE_ALIASES = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'rb': 'ruby',
    'sh': 'shell',
    'zsh': 'shell',
    'yml': 'yaml',
    'dockerfile': 'docker',
    'cs': 'csharp',
    'c++': 'cpp',
    'c#': 'csharp',
    'f#': 'fsharp',
    'obj-c': 'objective-c',
    'objc': 'objectivec',
    'tex': 'latex',
    'jsonc': 'json',
    'jsx': 'javascript',
    'tsx': 'typescript',
    'text': 'plain text',
    'txt': 'plain text',
    'ps1': 'powershell',
    'psm1': 'powershell',
};

// ── GitHub Alert → Emoji Map ───────────────────────────────────
const ALERT_EMOJI_MAP = {
    'NOTE': 'ℹ️',
    'TIP': '💡',
    'IMPORTANT': '❗',
    'WARNING': '⚠️',
    'CAUTION': '🔴',
};

// ── Rich Text Parser ───────────────────────────────────────────

/**
 * Splits text into ≤2000 character segments and pushes as
 * rich_text objects. Notion limits each rich_text content
 * to 2000 characters.
 */
function pushTextSegments(parts, content, annotations) {
    for (let i = 0; i < content.length; i += MAX_RICH_TEXT_LENGTH) {
        const segment = content.substring(
            i, i + MAX_RICH_TEXT_LENGTH
        );
        const obj = { type: 'text', text: { content: segment } };
        if (annotations) {
            obj.annotations = annotations;
        }
        parts.push(obj);
    }
}

/**
 * Parses inline Markdown formatting into Notion rich_text
 * objects. Supports: **bold**, *italic*, `code`,
 * ~~strikethrough~~, [link](url).
 *
 * Uses lazy matching (.+?) for bold/italic/strikethrough
 * to handle edge cases with special characters inside.
 */
function parseRichText(text) {
    const parts = [];
    const regex = /(\*\*.+?\*\*|~~.+?~~|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*(?!\s).+?(?<!\s)\*)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            pushTextSegments(
                parts,
                text.substring(lastIndex, match.index)
            );
        }

        const token = match[0];

        if (token.startsWith('**')) {
            pushTextSegments(
                parts,
                token.slice(2, -2),
                { bold: true }
            );
        } else if (token.startsWith('~~')) {
            pushTextSegments(
                parts,
                token.slice(2, -2),
                { strikethrough: true }
            );
        } else if (token.startsWith('`')) {
            pushTextSegments(
                parts,
                token.slice(1, -1),
                { code: true }
            );
        } else if (token.startsWith('[')) {
            const linkMatch = token.match(
                /^\[([^\]]+)\]\(([^)]+)\)$/
            );
            if (linkMatch) {
                parts.push({
                    type: 'text',
                    text: {
                        content: linkMatch[1],
                        link: { url: linkMatch[2] },
                    },
                });
            } else {
                pushTextSegments(parts, token);
            }
        } else if (token.startsWith('*')) {
            pushTextSegments(
                parts,
                token.slice(1, -1),
                { italic: true }
            );
        }

        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        pushTextSegments(parts, text.substring(lastIndex));
    }

    return parts.length > 0
        ? parts
        : [{ type: 'text', text: { content: text } }];
}

// ── Block Builders ─────────────────────────────────────────────

/**
 * Resolves a Markdown code fence language to a valid Notion
 * language string. Applies aliases and falls back to
 * 'plain text' for unknown languages.
 */
function resolveLanguage(lang) {
    const normalized = lang.toLowerCase().trim();
    if (NOTION_LANGUAGES.has(normalized)) {
        return normalized;
    }
    if (LANGUAGE_ALIASES[normalized]) {
        return LANGUAGE_ALIASES[normalized];
    }
    return 'plain text';
}

/**
 * Builds a Notion heading block (heading_1, heading_2,
 * or heading_3). Notion only supports 3 levels, so
 * levels 4+ are clamped to heading_3.
 */
function buildHeading(text, level) {
    const clampedLevel = Math.min(level, 3);
    const type = `heading_${clampedLevel}`;
    return { type, [type]: { rich_text: parseRichText(text) } };
}

/**
 * Builds a Notion code block with validated language
 * and auto-split rich_text segments.
 */
function buildCodeBlock(codeContent, lang) {
    const richText = [];
    for (
        let c = 0;
        c < codeContent.length;
        c += MAX_RICH_TEXT_LENGTH
    ) {
        richText.push({
            type: 'text',
            text: {
                content: codeContent.substring(
                    c, c + MAX_RICH_TEXT_LENGTH
                ),
            },
        });
    }
    if (richText.length === 0) {
        richText.push({ type: 'text', text: { content: '' } });
    }
    return {
        type: 'code',
        code: {
            rich_text: richText,
            language: resolveLanguage(lang),
        },
    };
}

/**
 * Builds a Notion callout block from a GitHub-style alert.
 */
function buildCallout(lines, alertType) {
    const emoji = ALERT_EMOJI_MAP[alertType] || 'ℹ️';
    return {
        type: 'callout',
        callout: {
            rich_text: parseRichText(lines.join('\n')),
            icon: { type: 'emoji', emoji },
        },
    };
}

/**
 * Builds a Notion quote block from blockquote lines.
 */
function buildQuote(lines) {
    return {
        type: 'quote',
        quote: {
            rich_text: parseRichText(lines.join('\n')),
        },
    };
}

/**
 * Builds a Notion to_do block from a task list item.
 */
function buildToDo(text, checked) {
    return {
        type: 'to_do',
        to_do: {
            rich_text: parseRichText(text),
            checked,
        },
    };
}

/**
 * Builds a Notion bulleted_list_item block.
 */
function buildBulletedListItem(text) {
    return {
        type: 'bulleted_list_item',
        bulleted_list_item: {
            rich_text: parseRichText(text),
        },
    };
}

/**
 * Builds a Notion numbered_list_item block.
 */
function buildNumberedListItem(text) {
    return {
        type: 'numbered_list_item',
        numbered_list_item: {
            rich_text: parseRichText(text),
        },
    };
}

/**
 * Builds a Notion table block from parsed rows.
 */
function buildTable(rows) {
    return {
        type: 'table',
        table: {
            table_width: rows[0].table_row.cells.length,
            has_column_header: true,
            has_row_header: false,
            children: rows,
        },
    };
}

// ── YAML Frontmatter Detection ─────────────────────────────────

/**
 * Detects and skips YAML frontmatter at the beginning of
 * the file. Frontmatter starts with '---' on line 0 and
 * ends with '---' on a subsequent line.
 *
 * Returns the index of the first line after the frontmatter,
 * or 0 if no frontmatter is detected.
 */
function skipFrontmatter(lines) {
    if (lines.length < 2 || lines[0].trim() !== '---') {
        return 0;
    }
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === '---') {
            return i + 1;
        }
    }
    return 0;
}

// ── Main Parser ────────────────────────────────────────────────

/**
 * Parses an array of Markdown lines into an array of
 * Notion API-compatible block objects.
 */
function parseMarkdown(lines) {
    const blocks = [];
    let i = skipFrontmatter(lines);

    while (i < lines.length) {
        const line = lines[i].trimEnd();
        const trimmed = line.trim();

        if (!trimmed) { i++; continue; }

        // ── Horizontal Rule ────────────────────────────────
        if (
            /^-{3,}$/.test(trimmed)
            || /^\*{3,}$/.test(trimmed)
            || /^_{3,}$/.test(trimmed)
        ) {
            blocks.push({ type: 'divider', divider: {} });
            i++;
            continue;
        }

        // ── Headings ───────────────────────────────────────
        if (/^#{1,6}\s/.test(trimmed)) {
            const level = trimmed.match(/^#+/)[0].length;
            const text = trimmed.replace(/^#+\s*/, '').trim();
            blocks.push(buildHeading(text, level));
            i++;
            continue;
        }

        // ── Code Blocks ────────────────────────────────────
        if (trimmed.startsWith('```')) {
            const lang = trimmed.slice(3).trim() || 'plain text';
            const codeLines = [];
            i++;
            while (
                i < lines.length
                && !lines[i].trim().startsWith('```')
            ) {
                codeLines.push(lines[i]);
                i++;
            }
            i++;
            blocks.push(
                buildCodeBlock(codeLines.join('\n'), lang)
            );
            continue;
        }

        // ── GitHub-style Alerts (> [!TYPE]) ────────────────
        if (trimmed.startsWith('> [!')) {
            const alertMatch = trimmed.match(/> \[!([A-Z]+)\]/);
            const alertType = alertMatch
                ? alertMatch[1]
                : 'NOTE';
            const calloutLines = [];
            i++;
            while (
                i < lines.length
                && lines[i].trim().startsWith('>')
            ) {
                const cl = lines[i].trim().replace(/^>\s*/, '');
                if (cl !== '') calloutLines.push(cl);
                i++;
            }
            blocks.push(buildCallout(calloutLines, alertType));
            continue;
        }

        // ── Blockquotes ────────────────────────────────────
        if (trimmed.startsWith('>')) {
            const quoteLines = [];
            while (
                i < lines.length
                && lines[i].trim().startsWith('>')
            ) {
                quoteLines.push(
                    lines[i].trim().replace(/^>\s*/, '')
                );
                i++;
            }
            blocks.push(buildQuote(quoteLines));
            continue;
        }

        // ── Task Lists (- [x] / - [ ]) ────────────────────
        if (/^[-*]\s\[[ xX]\]\s/.test(trimmed)) {
            const checked = /\[[xX]\]/.test(trimmed);
            const text = trimmed.replace(
                /^[-*]\s\[.\]\s*/, ''
            );
            blocks.push(buildToDo(text, checked));
            i++;
            continue;
        }

        // ── Bulleted Lists ─────────────────────────────────
        if (/^[-*]\s/.test(trimmed)) {
            const text = trimmed.replace(/^[-*]\s/, '');
            blocks.push(buildBulletedListItem(text));
            i++;
            continue;
        }

        // ── Numbered Lists ─────────────────────────────────
        if (/^\d+\.\s/.test(trimmed)) {
            const text = trimmed.replace(/^\d+\.\s/, '');
            blocks.push(buildNumberedListItem(text));
            i++;
            continue;
        }

        // ── Tables ─────────────────────────────────────────
        if (trimmed.startsWith('|')) {
            const rows = [];
            while (
                i < lines.length
                && lines[i].trim().startsWith('|')
            ) {
                const rowLine = lines[i].trim();
                if (/^\|[\s\-:|]+\|$/.test(rowLine)) {
                    i++;
                    continue;
                }
                const cells = rowLine
                    .split('|')
                    .slice(1, -1)
                    .map(c => c.trim());
                const notionCells = cells.map(
                    c => parseRichText(c)
                );
                rows.push({
                    type: 'table_row',
                    table_row: { cells: notionCells },
                });
                i++;
            }
            if (rows.length > 0) {
                blocks.push(buildTable(rows));
            }
            continue;
        }

        // ── Default: Paragraph ─────────────────────────────
        blocks.push({
            type: 'paragraph',
            paragraph: {
                rich_text: parseRichText(trimmed),
            },
        });
        i++;
    }

    return blocks;
}

// ── Chunking ───────────────────────────────────────────────────

/**
 * Splits an array of blocks into chunks of at most
 * CHUNK_SIZE blocks each.
 */
function chunkBlocks(blocks, chunkSize) {
    const chunks = [];
    for (let j = 0; j < blocks.length; j += chunkSize) {
        chunks.push(blocks.slice(j, j + chunkSize));
    }
    return chunks;
}

// ── Write Output ───────────────────────────────────────────────

/**
 * Writes chunk files to the output directory. Creates the
 * directory if it doesn't exist. Handles write errors
 * gracefully.
 */
function writeChunks(chunks, outDir) {
    try {
        if (!fs.existsSync(outDir)) {
            fs.mkdirSync(outDir, { recursive: true });
        }
    } catch (err) {
        console.error(
            `Error: Could not create output directory`
            + ` "${outDir}": ${err.message}`
        );
        process.exit(1);
    }

    chunks.forEach((chunk, idx) => {
        const filePath = path.join(outDir, `chunk_${idx}.json`);
        try {
            fs.writeFileSync(
                filePath,
                JSON.stringify(chunk, null, 2)
            );
        } catch (err) {
            console.error(
                `Error: Could not write file`
                + ` "${filePath}": ${err.message}`
            );
            process.exit(1);
        }
    });
}

// ── Execution ──────────────────────────────────────────────────

const lines = fs.readFileSync(inputFile, 'utf-8').split('\n');
const blocks = parseMarkdown(lines);
const chunks = chunkBlocks(blocks, CHUNK_SIZE);

writeChunks(chunks, outputDir);

console.log(
    `✅ Done — ${blocks.length} blocks`
    + ` → ${chunks.length} chunk(s)`
    + ` written to ${outputDir}`
);
