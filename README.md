# my-skills

AionUI / OpenCode / Cursor / Claude Code / Codex 等 Agent 平台的自定义技能仓库。

## 技能列表

| 技能 | 描述 |
|------|------|
| [production-readiness-audit](./skills/production-readiness-audit/) | 企业级工程成熟度与生产就绪审计。自主取证、Evidence First、Vibe Engineering 专项、GO/NO-GO 门禁；支持 `/audit-quick`（默认）、`/audit`、`/audit-security`、`/audit-vibe` 等模式 |
| [ppt-content-designer](./skills/ppt-content-designer/) | PPT 内容策划与设计规范生成器。将原始需求/文档转化为逐页内容大纲 + 视觉设计指引 |
| [uat-tester](./skills/uat-tester/) | 通用用户验收（UAT）测试体系执行器，框架无关、项目无关。先文档化角色矩阵与追溯矩阵，再落地自动化脚本（Playwright/WebdriverIO/Appium/Detox）。内建四条防回归原则：首屏零噪音、深链接抽屉覆盖、数据范围按角色隔离、幂等造数与隔离 |
| [project-docs-wiki](/yaocoder/my-skills/blob/main/skills/project-docs-wiki) | 把仓库工程 Markdown 做成 Docs-as-Code 资料库（VitePress）：文档治理 → 策展侧栏 → 一键本地预览 → CI 构建；避免 GitHub Wiki/Notion 双真相源 |

## 安装

### AionUI / OpenCode

#### 安装单个技能

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills/production-readiness-audit"}
JSON
```

#### 安装全部技能

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills"}
JSON
```

安装后记得将技能绑定到对应助手：

```bash
# 查看当前助手名称
"$AIONUI_HELPER_BIN" config assistants list

# 绑定技能（替换 <助手ID> 为实际 ID）
"$AIONUI_HELPER_BIN" config assistants update <<'JSON'
{
  "assistant_id": "<助手ID>",
  "enabled_skills": ["production-readiness-audit"]
}
JSON
```

> ⚠️ 技能绑定后仅对新会话生效，当前正在进行的会话不会自动加载。

### Cursor

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills

# 全局（所有项目可用）
mkdir -p ~/.cursor/skills
cp -r /tmp/my-skills/skills/production-readiness-audit ~/.cursor/skills/

# 或项目级（仅当前仓库）
mkdir -p .cursor/skills
cp -r /tmp/my-skills/skills/production-readiness-audit .cursor/skills/
```

新开 Chat 或重载窗口后，在目标项目中说 `/audit-quick` 或「评估工程成熟度」即可触发。

### Claude Code

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
mkdir -p ~/.claude/skills
cp -r /tmp/my-skills/skills/production-readiness-audit ~/.claude/skills/
```

### Codex

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
mkdir -p ~/.agents/skills
cp -r /tmp/my-skills/skills/production-readiness-audit ~/.agents/skills/
```

## 更新

```bash
cd /tmp/my-skills && git pull

# AionUI：重新导入（会覆盖更新）
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills/production-readiness-audit"}
JSON

# Cursor / Claude Code / Codex：重新复制对应目录
cp -r /tmp/my-skills/skills/production-readiness-audit ~/.cursor/skills/
```

## 添加新技能

1. 在 `skills/` 下创建子目录：`mkdir -p skills/<技能名>`
2. 放入 `SKILL.md`（必需）；复杂技能可加 `references/`、`scripts/` 等 bundled resources
3. 更新本 README 的技能列表与安装说明
4. 提交推送：

```bash
git add skills/<技能名> README.md
git commit -m "feat: add <技能名> skill"
git push
```

## 技能结构要求

```
skills/
└── <技能名>/
    ├── SKILL.md              # 技能定义（YAML frontmatter + Markdown，必需）
    └── references/           # 可选：按需加载的参考文档
        └── *.md
```

`SKILL.md` 需包含 YAML frontmatter，定义技能名称和描述：

```yaml
---
name: <技能名>
description: >
  技能描述，说明何时触发该技能
---
```

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

- [AionUI](https://aionui.com)
- [Cursor Skills 文档](https://docs.cursor.com)
