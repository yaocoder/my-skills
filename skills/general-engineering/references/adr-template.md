# ADR

一条决策一份文件。给不可轻易反悔的选择留出处，并挂上可检查验收。

## 文件

`docs/决策记录/NNNN-短标题.md`

索引：`docs/决策记录/README.md`（编号、标题、状态）。

## 模板

```markdown
# ADR-NNNN 标题

- 状态：Proposed | Accepted | Superseded | Deprecated
- 日期：YYYY-MM-DD

## 背景 Context

要解决的问题与约束（规模、团队、交付期限）。

## 决策 Decision

选了什么。

## 备选 Alternatives

未选方案与原因。

## 约束 Constraints

人与 Agent 必须遵守的硬规则（模块边界、禁止跨模块直访表、密钥不进客户端等）。

## 迁移 Migration

若替换旧方案，步骤与兼容窗口。无则写「无」。

## 验收 Acceptance

可检查项，例如：

- 测试名 / ArchUnit 或等价边界测试
- grep 规则
- CI job 名
- 命名 E2E / 脚本路径
```

## 新仓首条建议

未指定架构时，写 **ADR-0001 模块化单体（或选定形状）**：

- 默认单体 + 模块切线
- 拆服务的触发条件（团队/发布节奏/扩展瓶颈）写清楚
- 验收：无跨模块直接改表；空 `services/*` 不得宣称已拆分
