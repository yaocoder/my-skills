---
name: project-docs-wiki
description: >
  Turn a repo's engineering Markdown into a Docs-as-Code wiki (curated nav,
  search, one-click local preview, CI build). Use whenever the user asks for
  a wiki, 资料库, 知识库, documentation site, VitePress/MkDocs, docs cleanup
  plus site, GitHub Wiki, one-click wiki start, or to organize/merge/archive
  docs/ so people can browse it. Even if they only say 「把文档做成站点」
  or 「工程资料怎么查」, follow this skill instead of dumping files into
  GitHub Wiki or Notion as a second source of truth.
---

# Project Docs Wiki

把仓库里已有的工程 Markdown 做成**可检索、可预览、跟 git 同版本**的资料库。站点只渲染，不另起一份正文。

本技能来自多次真实落地：先治理文档，再挂 VitePress，再给一键启动与 CI 门禁。跳过治理直接搭站，侧栏会变成垃圾场。

## When this applies

- 用户要 wiki / 资料库 / 知识库 / 文档站点
- 用户要整理 `docs/`：删冗余、归档过时、合并重复、修断链
- 用户要本地预览、一键启动、CI 构建文档站
- 用户提到 GitHub Wiki / Notion / Confluence 当工程文档主站（改成 Docs-as-Code）

## Defaults (do not reopen unless user insists)

| Decision | Default | Why |
|----------|---------|-----|
| Stack | **VitePress** on existing `docs/` | Vue/pnpm repos; Markdown stays in place |
| Source of truth | git Markdown | Dual copies drift |
| Hosting phase 1 | `docs:dev` / `docs:build` + CI; **no** public Pages, **no** prod `/wiki/` | Ship browseable wiki first |
| Nav | **Curated** sidebar by layer | Full auto-nav of every file is unusable |
| GitHub Wiki | Do not use as primary | Separate git, weak review, weak access split |

If the repo is Python-only with no Node, MkDocs Material is acceptable. Do not invent a third stack.

---

## Workflow (run in order)

### 1. Inventory, do not start with config

Read `docs/` (or whatever the repo uses). Classify every tree into **three layers**:

1. **Canonical** — product, architecture, API, test, ops (people should find these)
2. **External** — commercial, marketing, partner/custom (fold in nav)
3. **Process** — Q&A, session logs, `_archive/`, generated specs (entry only, not every file)

Also note: package manager, existing start scripts and ports, CI file, whether `docs/` already has a site.

If `docs/` is chaos, **clean before VitePress**. A pretty site on duplicate/outdated pages trains people to distrust docs.

### 2. Cleanup (high confidence only)

Do these; skip heroic rewrites of valid history.

**Delete** only empty stubs, 3-line pointers to a canonical doc, and zero-value rename notes.

**Archive** (move to that folder's `_archive/` + README) thin placeholders and superseded runbooks. Prefer archive over hard-delete for numbered product docs.

**Merge** same-day / same-theme short session notes into one file; update indexes. Do not merge unrelated bugs just because they are short.

**Move** files that sit in the wrong time bucket (e.g. August notes still in a Q3 dump).

**Renumber** when two docs share the same sequence number.

**Fix links** after moves. Scan relative Markdown links; rewrite:
- files moved into monthly/quarter folders
- docs relocated (`RESS` out of product-planning, etc.)
- `file://` absolute paths → repo-relative
- missing indexes → add `README.md` for directories the sidebar will open

Do **not** mass-delete process history or implementation archives just to look tidy.

Write a short process note in the repo's session-log convention (if none exists, `docs/` changelog or `YYYY-MM-DD-docs-wiki.md`).

### 3. Maintenance rule (so the wiki does not rot)

Add a **document maintenance** page and link it from the docs index. It must say:

- One source of truth: git Markdown; the site only renders
- Where new files go (by layer / directory)
- Update in place vs archive when a design is replaced
- New canonical page → update directory README **and** VitePress sidebar if it should appear in nav
- No secrets, tokens, or customer host passwords in docs the site will build
- Checklist at the end of the file

Do not copy a retail-specific folder tree into an unrelated repo. Infer directories from **this** repo, then write the table.

Template: [references/maintenance-guide.md](references/maintenance-guide.md)

### 4. VitePress on existing docs (no second content tree)

```
docs/
  .vitepress/config.mts
  index.md          # wiki home; keep docs/README.md for GitHub
  ...unchanged Markdown
```

- `rewrites`: `:folder/README.md` → `:folder/index.md` (and one nested level). **Do not** rewrite root `README.md` to `index.md` if both exist — they fight.
- Root `index.md` = wiki landing (layers + how to preview).
- `base: '/'` in phase 1.
- `ignoreDeadLinks: true` in phase 1 after you have added missing directory READMEs. Historical docs always link to `apps/`, `CHANGELOG`, binaries, `reference/` gitignored trees. Failing CI on those blocks the wiki for no product value. Still fix links you **created** or **broke** in this change.
- `search.provider: 'local'`.
- Sidebar groups: 入门 → 正式(精选) → 对外(collapsed) → 过程(Q&A + session-log **entry only**).
- `_archive/` and bulk session logs stay off the main sidebar.

Copy and adapt: [references/vitepress-config.md](references/vitepress-config.md)

### 5. Package scripts and gitignore

Root `package.json` (or the docs package if the repo already isolates it):

```json
"docs:dev": "vitepress dev docs",
"docs:build": "vitepress build docs",
"docs:preview": "vitepress preview docs"
```

devDependency: `vitepress` (current 1.x).

gitignore:

```
docs/.vitepress/dist/
docs/.vitepress/cache/
```

Install with the repo's package manager (`pnpm add -Dw vitepress` when the repo is pnpm).

### 6. One-click start script

Do not tell people to run `pnpm docs:dev` as the only entry. VitePress default port **5173** collides with typical Vite/uni-app apps.

Add `./start-wiki.sh` at repo root:

- Default port **5177** (or the first free port above the app range); `WIKI_PORT` / `WIKI_HOST`
- `--fg` / `--stop` / `--status`; background by default
- PID + log under `.local-run/` (or the repo's existing local-run dir)
- **Never** use `vitepress --version` as a health check — some versions start `dev`
- Detect vitepress via `node_modules/vitepress/package.json`; install if missing
- macOS `open` the URL unless `NO_OPEN=1`

Copy from [scripts/start-wiki.sh](scripts/start-wiki.sh) and replace package-manager invocations if the repo is npm/yarn.

Wire the script into the ops/docs index so it is discoverable.

### 7. CI gate

Add a job that only does install + `docs:build` (or `npm run docs:build`). Fail the PR if the wiki does not build. Do not attach Pages deploy in phase 1.

### 8. Verify

```bash
./start-wiki.sh          # HTTP 200 on the chosen port
./start-wiki.sh --stop
pnpm docs:build          # or npm/yarn equivalent
```

Sidebar must reach: maintenance guide, architecture or equivalent canonical area, ops, Q&A.

---

## What not to do

- GitHub Wiki or Notion as a **second** body of docs
- Auto-sidebar of every Markdown file including archives and daily logs
- Putting secrets into the static site
- Rewriting all historical Markdown structure just to please the generator
- Public GitHub Pages / production Nginx `/wiki/` unless the user explicitly asks for phase 2
- Starting `vitepress --version` in scripts

---

## Phase 2 (only if asked)

GitHub Pages (`base` = repo name) or Nginx subpath (`base: '/wiki/'`). Still no dual editing on the host.

---

## Test prompts (for later eval)

1. 「把这个仓库的 docs 做成 wiki 资料库」
2. 「文档又乱了，整理后再能本地打开检索」
3. 「不要 GitHub Wiki，用现有 Markdown 做站点，还要一键启动」
