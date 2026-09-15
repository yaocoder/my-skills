# my-skills

跨 Agent 客户端的自定义技能仓库。基于 [Agent Skills](https://github.com/vercel-labs/skills) 开放标准，可用 `npx skills` 一键安装到 Cursor、Claude Code、Codex、Gemini CLI、OpenCode、CodeBuddy、Trae、Qoder 等 40+ 客户端。

## 技能列表

| 技能 | 描述 |
|------|------|
| [general-engineering](./skills/general-engineering/) | 领域中立的软件工程承载面：新仓 bootstrap、已有仓 harden、对照价值流出缺口。含目录骨架、文档 taxonomy/索引、ADR、本地 start/stop、env 分层、CI guard、ops/deploy 契约、AGENTS.md 与审计槽位。正式 GO/NO-GO 仍走 `production-readiness-audit` |
| [production-readiness-audit](./skills/production-readiness-audit/) | 企业级工程成熟度与生产就绪审计。自主取证、Evidence First、Vibe Engineering 专项、GO/NO-GO 门禁；支持 `/audit-quick`（默认）、`/audit`、`/audit-security`、`/audit-vibe` 等模式 |
| [ppt-content-designer](./skills/ppt-content-designer/) | PPT 内容策划与设计规范生成器。将原始需求/文档转化为逐页内容大纲 + 视觉设计指引 |
| [uat-tester](./skills/uat-tester/) | 通用用户验收（UAT）测试体系执行器，框架无关、项目无关。先文档化角色矩阵与追溯矩阵，再落地自动化脚本（Playwright/WebdriverIO/Appium/Detox）。内建四条防回归原则：首屏零噪音、深链接抽屉覆盖、数据范围按角色隔离、幂等造数与隔离 |
| [project-docs-wiki](./skills/project-docs-wiki/) | 把仓库工程 Markdown 做成 Docs-as-Code 资料库（VitePress）：文档治理 → 策展侧栏 → 一键本地预览 → CI 构建；避免 GitHub Wiki/Notion 双真相源 |

## 安装（推荐：npx skills）

前置：已安装 Node.js（含 `npx`）。安装器会把技能放到各客户端对应目录，**新开会话**后生效。

### 常用命令

| 目的 | 命令 |
|------|------|
| 列出本仓库全部技能 | `npx skills add yaocoder/my-skills -l` |
| 交互安装（选技能 + 选客户端） | `npx skills add yaocoder/my-skills` |
| 全局安装全部技能到全部已检测客户端 | `npx skills add yaocoder/my-skills -g --all` |
| 全局只装一个技能到 Cursor | `npx skills add yaocoder/my-skills -g -a cursor -s production-readiness-audit -y` |
| 全局装到多客户端 | `npx skills add yaocoder/my-skills -g -a cursor -a claude-code -a codex -y` |
| 项目级安装（在目标仓库根目录执行） | `npx skills add yaocoder/my-skills -s uat-tester -y` |
| 查看已安装技能 | `npx skills list -g` |
| 更新已安装技能 | `npx skills update -g -y` |
| 卸载某个技能 | `npx skills remove -g -s production-readiness-audit -y` |

### 按客户端示例

```bash
# Cursor（全局）
npx skills add yaocoder/my-skills -g -a cursor -y

# Claude Code（全局）
npx skills add yaocoder/my-skills -g -a claude-code -y

# Codex（全局）
npx skills add yaocoder/my-skills -g -a codex -y

# Gemini CLI / OpenCode / CodeBuddy / Trae / Qoder
npx skills add yaocoder/my-skills -g -a gemini-cli -y
npx skills add yaocoder/my-skills -g -a opencode -y
npx skills add yaocoder/my-skills -g -a codebuddy -y
npx skills add yaocoder/my-skills -g -a trae -y
npx skills add yaocoder/my-skills -g -a qoder -y
```

> `-a` 取值以 `npx skills` 当前支持列表为准；不确定时用交互安装，或 `-g --all` 装到本机已检测到的全部客户端。

### 范围说明

| 范围 | 何时用 | 效果 |
|------|--------|------|
| **全局**（`-g`） | 个人常用技能 | 写入用户目录（如 `~/.cursor/skills/`、`~/.claude/skills/`），所有项目可用 |
| **项目级**（不加 `-g`） | 团队共享、仓库内约定 | 写入当前仓库（如 `.agents/skills/`），随仓库分发 |

安装后请 **新开 Chat / 新开 session**；已有会话不会自动加载新技能。

## 添加新技能

1. 在 `skills/` 下创建子目录：`mkdir -p skills/<技能名>`
2. 放入 `SKILL.md`（必需）；复杂技能可加 `references/`、`scripts/` 等 bundled resources
3. 更新本 README 的技能列表与快速用法
4. 提交推送：

```bash
git add skills/<技能名> README.md
git commit -m "feat: add <技能名> skill"
git push
```

本地验证能否被 CLI 发现：

```bash
npx skills add ./ -l
# 或
npx skills add yaocoder/my-skills -l
```

## 技能结构要求

```
skills/
└── <技能名>/
    ├── SKILL.md              # 技能定义（YAML frontmatter + Markdown，必需）
    ├── references/           # 可选：按需加载的参考文档
    └── scripts/              # 可选：可执行辅助脚本
```

`SKILL.md` 需包含 YAML frontmatter：

```yaml
---
name: <技能名>
description: >
  技能描述，说明何时触发该技能
---
```

目录布局兼容 `npx skills` 的发现规则：`skills/<name>/SKILL.md`。

## general-engineering 快速用法

在目标仓库对 Agent 说：

| 说法 | 行为 |
|------|------|
| 「按软件工程体系建项目」 | bootstrap：中立骨架 + 文档索引 + ADR + 本地 DX + CI/deploy 槽位 |
| 「这个仓太乱，帮我工程化一下」 | harden：补缺口，拆穿虚假成熟度，不推翻能跑的布局 |
| 「对照需求-开发-测试-验收-发布-运营出缺口」 | align-audit：只出清单，默认不改代码 |
| `/general-engineering` | 显式触发本技能 |

不绑业务域。正式上线裁决请用 `production-readiness-audit`。

## production-readiness-audit 快速用法

在已安装 skill 的项目仓库中，对 Agent 说：

| 命令 / 说法 | 模式 |
|-------------|------|
| `/audit-quick` 或「快速审计」 | 默认：先找 P0/P1 与上线 blocker |
| `/audit` | 完整 21 阶段审计 |
| `/audit-production` | 临上线：Security / Deploy / Backup / Rollback |
| `/audit-security` | 安全专项 |
| `/audit-vibe` | Vibe Coding / AI 工程债务专项 |

审计默认 **只读**，不写业务代码；允许在 `.audit/` 下生成报告。

## project-docs-wiki 快速用法

在目标仓库对 Agent 说：

| 说法 | 行为 |
|------|------|
| 「做资料库 / wiki / 知识库」 | 按技能：盘点 → 治理 → VitePress → `start-wiki.sh` → CI |
| 「整理 docs/」 | 先治理再挂站，不跳过归档/断链修复 |
| `/project-docs-wiki` | 显式触发本技能 |

默认：VitePress 挂现有 `docs/`；站点只渲染，不另起正文真相源。

## 相关资源

- [vercel-labs/skills](https://github.com/vercel-labs/skills) — `npx skills` 安装器与 Agent Skills 生态
- [skills.sh](https://skills.sh) — 技能发现与浏览
- [Cursor Skills 文档](https://cursor.com/docs/skills)
