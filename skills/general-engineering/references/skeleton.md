# 目录骨架

按**运行时角色**分区。先立骨架再填实现。

## 默认变体（多端 + 服务）

```text
repo/
  apps/                 # 可部署客户端
  packages/             # 无副作用共享库
  services/             # BFF / 领域服务 / worker
  deploy/               # 目标机安装 footprint（路径稳定 = 契约）
  ops/                  # 运维编排（人侧，可改）
  docs/                 # 正式知识
  scripts/              # 本地辅助（可并入 ops/scripts）
  tests/                # 仅当测试不跟服务走时；否则别留空根 tests/
  .github/workflows/
  .githooks/            # 可选，钩子必须轻
  .audit/               # 槽位；正式报告由审计技能写
  .cursor/rules/        # 可选硬约束
  AGENTS.md
  README.md
  start.sh stop.sh status.sh   # 或 scripts/ 下等价物
  .env.example
```

## 其它变体（跟随已有栈，不要混用）

| 形状 | 何时 |
|------|------|
| `frontend/` + `backend/` + `worker/` | 模块化单体 + 独立计算进程 |
| `services/` + `packages/` + `sdk/` | 多语言多服务，且确实已有第二服务 |
| 单包应用 | 小工具：`src/` + `docs/` + `scripts/`，不要空 `apps/` `services/` |

未证明需要拆分时，优先模块化单体目录（backend 多模块），把切线写进 ADR。

## 规则

- **根瘦**：`deploy-remote-*.sh` 一类只做转发。
- **`deploy/` 不随心情改名。** 远端 unpack 依赖稳定路径。
- **`packages/` 环境无关**：不放仅浏览器或仅 Node 的 API。
- **测试目录单一真相**：要么根 `tests/` 有说明并真正使用，要么测试住在各模块内，根 README 写「测试在哪跑」。禁止根 `tests/` 空目录假装有体系。
- 每个空模块 `README.md` 第一行：`status: planned | active`。
