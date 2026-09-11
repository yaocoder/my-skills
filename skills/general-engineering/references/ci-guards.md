# CI、测试槽位、DoD

分层门禁：小而硬的 guard 不被全量红套件淹没。文档里写了的检查必须接线，否则标缺口。

## CI 分层

| 层 | 内容 | 策略 |
|----|------|------|
| Guard | 密钥形态、demo 凭据进 prod 构建、静默吞错、架构边界 | 全分支；失败即红 |
| 语言矩阵 | 单测、typecheck | 按栈并行 |
| 依赖审计 | 可选 SCA | 可先 report |
| E2E/UAT | clean 栈关键旅程 | 可后加；深用例交 uat-tester |
| 软门 | 历史债 | 文档写清何时变硬 |

全分支跑 CI。只护 `main` 等于日常无门禁。

本地钩子若做：只跑 guard，十秒量级。过重会逼 `--no-verify`。

## 测试槽位

在 README / AGENTS / `docs/运维` 或测试说明里写清**一条命令**：

- 单测（各语言入口）
- 类型检查
- （可选）`tests/performance/` status: planned
- 功能/UAT：链接到方案或写「使用 uat-tester 建立」

根 `tests/` 空目录且真实测试在模块内 = 分裂大脑。二选一写死。

## Guard 雏形（L1）

新仓至少选能自动查的 1–2 条，例如：

- 禁止把 `.env` 列入提交（gitignore + 可选 CI 扫描）
- 生产 Dockerfile/compose 不含演示密码
- 客户端包不含第三方 secret 环境变量名

上线更硬的 guard 前，用一条故意失败的例子证明能拦住（植入回归），把证明链到 CI 文档。写进文档却从未红过的门禁不可信。

## DoD 示例条目（改成项目可执行命令）

- `start` 后 status 健康
- 单测命令退出 0
- 迁移与 API 契约有变更时有对应文件
- `verify` 脚本（或清单）已执行
- 密钥未进 git
