---
name: general-engineering
description: >-
  在 git 仓库内建立、整顿或对齐一套领域中立的软件工程承载面：目录骨架、文档 taxonomy 与索引、ADR、本地 start/stop、env 分层、CI guard、ops/deploy 契约、AGENTS.md、测试/制品/DoD 槽位、观测阶梯与审计包。当用户要按软件工程体系建项目、脚手架新仓、工程化落地、整顿已有仓库的文档/CI/部署、bootstrap monorepo、补工程底座、或把仓库对齐「需求-开发-测试-验收-发布-运营」价值流时必须使用。即使用户只说「按规范建个项目」「这个仓太乱帮我工程化一下」「先把工程体系搭起来」，也应触发。不要用于产品/业务架构方案、生产 GO/NO-GO 审计、只写一条 Cursor rule、或只创建 git remote。
---

# General Engineering System

在仓库里落下**可支撑价值流的工程承载面**，不写业务功能，不绑行业域。

目标不是「看起来像大厂仓库」，而是：人与 Agent 能一键跑起来、文档找得到、约束能被 CI/脚本检查、交付路径诚实、未就绪的能力不装成已就绪。

## 何时读哪份参考

按需打开，不要一次读完：

| 场景 | 读 |
|------|-----|
| 任何模式开始前 | `references/maturity-levels.md`，再读 `references/value-stream.md` |
| 定目录 / 选变体 | `references/skeleton.md` |
| 写文档体系 | `references/docs-taxonomy.md` |
| 写或补 ADR | `references/adr-template.md` |
| 本地启动与环境 | `references/local-dx.md` |
| CI / 测试槽位 | `references/ci-guards.md` |
| 安装包与发布回滚 | `references/deploy-contract.md` |
| Agent 入口 | `references/agents-md.md` |
| 审计槽位或缺口清单 | `references/audit-pack.md` |

## 与其它技能的边界

本技能**建/补仓内工程系统**。做完可交接，不要吞掉邻居的职责：

| 用户其实要的是 | 改用 / 随后调用 |
|----------------|-----------------|
| 只建 Cursor 托管远程、备份分享 | `new-repo` / `share` / `origin` |
| 只写 `.cursor/rules` 或单条 AGENTS 约定 | `create-rule`（本技能可建议需要哪些 rule，不替代它） |
| 深 UAT：角色矩阵、越权、首屏零噪音自动化 | 槽位按本技能留下后，交 `uat-tester` |
| 本地点测已有 Web UI | `webapp-testing` |
| 已有仓能否上生产、GO/NO-GO | `production-readiness-audit`（只读 `.audit/`） |
| 把已有 Markdown 做成 wiki 站点 | `project-docs-wiki` |
| 某业务域的产品/平台架构 | 领域技能；本技能只提供中立槽位 |

冲突时：本技能先保证承载面；领域内容写进 `docs/产品/` 等槽位，不反向污染骨架命名。

## 三种模式

根据用户意图选一个，**先声明再执行**：

1. **bootstrap** — 新仓或空目录。落到成熟度 L0，并预留 L1 槽位。不实现业务功能。
2. **harden** — 已有仓。只补缺口，不推翻能跑的布局；空脚手架标 `planned`，不假装能力已有。
3. **align-audit** — 对照价值流与成熟度做缺口清单。默认**不改代码**；用户明确说「按清单改」再转入 harden。需要正式 GO/NO-GO 时停手，改走 `production-readiness-audit`。

不确定就问一句：新仓 / 整顿 / 只出缺口清单。用户已说清则不要问。

## 硬约束（解释为何）

工程技能最容易制造**虚假成熟度**：目录很全、门禁是空的。三仓踩过的坑都从这里来。

- **领域中立。** 骨架与文档分类用通用名（apps/services/docs），不用行业词当顶层目录。
- **权威单一。** 同类信息一个真相源；别处只链过去。改路径必改文档索引。
- **约束要能检查。** ADR/DoD/密钥规则若写了，同步落到脚本、测试或 CI；落不了就写进延期清单，不要只写在 Markdown。
- **空目录 ≠ 能力。** `helm/`、`services/foo` 只有 README 时，标题或 README 标明 `status: planned`。
- **R&D 可演示 ≠ Prod GA。** demo 密钥路径与 prod 分离；默认口令进生产必须能被门禁拦住。
- **文档承诺必须接线。** 写了 lint/typecheck 却不进 CI，视为缺口，不是「已有规范」。
- **根目录保持瘦。** 远程安装路径（`deploy/`）是契约，不随意搬；编排脚本进 `ops/`，根上只留薄 wrapper。
- **不生成组织流程空文。** 不写价值评审会章程、看板 SOP、OKR 仪表盘。价值流图只用来对齐仓内产物。

## 工作流

### 0. 侦察

- bootstrap：看目标路径是否为空、技术栈是否已指定。未指定则选最小可变体（见 `skeleton.md`），不要默认微服务。
- harden / align-audit：扫根目录、`docs/`、CI、compose/scripts、`.env*.example`、`AGENTS.md`。用证据说话，不凭 README 宣称。

### 1. 定成熟度目标

读 `maturity-levels.md`。默认：

- 新仓 → **L0 可跑** + L1 槽位（DoD、deploy 契约、CI 最小）
- 整顿 → 在现有水平上补**下一档 P0**，一次不要跳到 L2 全家桶

把目标写进给用户的执行摘要。压测、混沌、三层监控、灰度：**默认关闭**，除非用户点名或已有移动端/生产包。

### 2. 按模式落地

**bootstrap 最低交付（L0 + L1 槽位）：**

1. 目录骨架 + 根 `README.md`（结构、start/stop、文档入口、ADR 入口）
2. `docs/` taxonomy + `docs/文档索引.md`（或 `docs/README.md` 作唯一导航）
3. ADR 目录 + 模板 + 可选 ADR-0001（模块化单体 vs 多服务：未证明规模前优先单体）
4. `.gitignore`（密钥、`.run/`、`log/`、构建物）
5. `.env.example`（及 prod/test example 槽位）；统一环境变量前缀
6. `start` / `stop` / `status`（或明确暂缓原因 + 命令表仍写在 README）
7. `AGENTS.md`（命令与硬约束与脚本同源）
8. CI 最小：能跑的检查就接线；接线不了的标缺口
9. `deploy/` + `ops/` 槽位 + `verify`/`rollback` 意识（脚本可以是 stub，但路径稳定、README 说明状态）
10. 测试槽位说明（单测入口；UAT 指向 `uat-tester`，不在本技能展开用例）
11. `.audit/README.md` 槽位（解释何时请审计技能）

**harden：** 出一张缺口表（有 / 无 / 虚假成熟度），按 P0→P1 补文件。不重构业务代码。不把 FAQ 写成能力 SSOT。

**align-audit：** 只出缺口清单，映射到价值流阶段与成熟度。格式见 `audit-pack.md` 的 gap 模板。

### 3. 收尾报告

完成后用下面结构回复（路径用真实路径）：

```markdown
## 模式与目标
模式：bootstrap | harden | align-audit
成熟度目标：L0 / L1 / L2
技术栈变体：…

## 已落下
- path — 一句话用途

## 槽位 / planned
- path — 为何暂缓

## 刻意不做
- 项 — 原因（虚假成熟度 / 属其它技能 / 用户未要求）

## 下一步（人来选）
- 例如：补真实 CI 门禁；调用 uat-tester；调用 production-readiness-audit
```

## 技术栈未定时的默认

- 未指定语言：只建**中立骨架 + 文档 + 脚本接口**，用注释标明「按实际栈替换」；不要发明一套用户没要的微服务。
- 未证明流量与团队规模：默认**模块化单体切线**（模块边界、表前缀意识、禁止跨模块直访），把「将来拆服务」写进 ADR，而不是先建空 `services/*`。
- 已有栈：跟随仓库，不强行 pnpm/Maven/Turbo。

## Cursor 规则

需要「每次对话都遵守」的约定（文档目录归属、密钥不进客户端）时，列出建议的 rule 文件名与要点，提醒用户可用 `create-rule` 固化。本技能可以直接写下 `.cursor/rules/*.mdc` **仅当用户已要求写规则或正在 bootstrap 且 AGENTS.md 需要硬约束落地**。
