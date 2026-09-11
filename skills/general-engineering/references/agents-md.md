# AGENTS.md

给 Agent 与新人的入场说明书。命令必须与真实脚本、`package.json`、Makefile **同源**；改脚本必改本文。

可选再镜像一份 `CLAUDE.md`，内容对等，禁止分叉。

## 建议章节

1. 一句话：仓库是什么（无营销）
2. 目录地图（链骨架）
3. 本地如何跑（start/stop/status）
4. 测试与 CI（guard vs full）
5. 文档从哪读（索引链接）
6. 硬约束（密钥、空脚手架、跨模块表、客户端无第三方密钥）
7. 提交约定
8. 相关：ADR 索引、运维索引、`.cursor/rules`

## 硬约束要短

写「永不重犯」级。细节进 rule 或 ADR。

建议 bootstrap 带上的几条：

- 不提交真实密钥
- 不把 planned 目录当成已交付能力对外描述
- 改 `docs/` 路径必须改索引
- 生产配置拒绝演示默认值

## 与 create-rule

需要 alwaysApply 的目录归属、密钥边界，用 `.cursor/rules/*.mdc`。本参考不展开 mdc 语法。
