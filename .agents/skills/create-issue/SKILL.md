---
name: create-issue
description: Create a new issue as a Markdown file in the issues/ folder with YAML front matter, ready to be published via gh CLI. Use when the user asks to capture, write, file, log, or record an issue.
---

# Create Issue

Create a new issue as a Markdown file in the `issues/` folder. The file follows a strict naming convention and YAML front matter template, and can later be published to GitHub via the `gh` CLI.

## File Naming Convention

Format: `XXX.slug.md`

- **`XXX`** — a zero‑padded, incrementing number with at least three digits (e.g., `001`, `010`, `100`).
  - Scan `issues/*.md` files in the repository root, extract the leading number from each filename, take the maximum, and add 1.
  - If the `issues/` folder is empty or does not exist, start at `001`.
- **`slug`** — a short, human-readable identifier derived from the issue title.
  - Use only lowercase letters, digits, and hyphens.
  - Keep it concise (e.g., `add-login-button`, `fix-typo`).

Examples: `001.task1.md`, `010.task2.md`, `025.fix-typo.md`.

## File Template

Each file must contain a YAML front matter block followed by the issue description in Markdown.

```markdown
---
title: "Brief, descriptive title"
project: "Optional project name or URL"
milestone: "Optional milestone title"
labels:
  - label-one
  - label-two
---
Detailed description of the issue.

Use full Markdown here: lists, code blocks, task lists, etc.
```

### Field Notes

- **`title`** (required): The exact title for the GitHub issue. Wrap in double quotes.
- **`project`** (optional): The project board to associate the issue with. Can be a project name or a URL (e.g., `"My Project"` or `"https://github.com/org/repo/projects/1"`). Omit or leave blank if not needed.
- **`milestone`** (optional): The milestone name. Omit or leave blank if none.
- **`labels`** (optional): A YAML list of label names to apply. Use an empty list `[]` if no labels are wanted.
- The **body** (everything after the second `---`) becomes the issue description. It can contain any valid Markdown.

## Usage

### 1. Determine the next issue number

```bash
# From the repository root
ls issues/*.md 2>/dev/null | sed 's|issues/||; s|\..*||' | sort -n | tail -1
```

If the command produces no output, the next number is `001`. Otherwise, add 1 to the output and zero-pad to at least three digits.

### 2. Create the issue file

Write the file to `issues/<next-number>.<slug>.md` following the template above.

### 3. Publish to GitHub with the `gh` CLI (optional)

Once the file is ready, publish it:

```bash
# Ensure you are in the repository root

TITLE=$(yq '.title' issues/XXX.slug.md)
LABELS=$(yq '.labels | join(",")' issues/XXX.slug.md)
MILESTONE=$(yq '.milestone' issues/XXX.slug.md)
PROJECT=$(yq '.project' issues/XXX.slug.md)
BODY=$(sed '1,/^---$/d' issues/XXX.slug.md)

gh issue create \
  --title "$TITLE" \
  --body "$BODY" \
  --label "$LABELS" \
  ${MILESTONE:+--milestone "$MILESTONE"} \
  ${PROJECT:+--project "$PROJECT"}
```

Replace `XXX.slug.md` with the actual filename.

If `yq` is not available, parse the file directly in code (e.g., split on `---` and extract front matter fields).

## Example

**File:** `issues/042.implement-dark-mode.md`

```markdown
---
title: "Implement dark mode toggle"
project: "UI Overhaul"
milestone: "v2.1"
labels:
  - enhancement
  - frontend
---
Add a toggle in the settings page to switch between light and dark themes.

- [ ] Add CSS variables for dark theme
- [ ] Build a `ThemeToggle` component
- [ ] Persist user preference in localStorage
```

This would result in an issue titled "Implement dark mode toggle" with labels `enhancement, frontend`, milestone `v2.1`, and project `UI Overhaul`.