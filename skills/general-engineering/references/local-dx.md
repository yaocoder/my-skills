# 本地 DX 与 env 分层

本地若跑不起来，CI 与文档都会漂。密钥分层失败会把 demo 便利变成生产事故。

## start / stop / status

| 命令 | 行为 |
|------|------|
| start | 起依赖与进程；等端口；日志 tee 到 `log/` |
| stop | 按 PID 或 compose 干净停 |
| status | PID、端口、健康摘要 |

约定：

- `.run/` 存 PID（gitignore）
- `log/run_YYYYMMDD_HHMMSS_<id>.log`
- 端口预检；`*.local.env` 覆盖个人端口
- 失败必须非零退出码

进阶（harden，非 bootstrap 必做）：

- `restart <layer>` 只重启一层
- 双栈：demo（种子数据）vs clean（近生产）；UAT/CI 走 clean

无应用代码时：仍提供脚本接口或在 README 写「L0 仅骨架，start 待应用」。不要提交永远 `exit 0` 却声称已启动的假脚本。

## env 分层

只把 example 进 git：

```text
.env.example
.env.production.example
.env.test.example
.deploy.env.example          # 运维/SSH 侧，与应用 env 分开
*.local.env                  # gitignore
```

原则：

- **统一前缀**（如 `APP_*`），跨语言同一名字。
- **prod 拒默认值**：发现 `changeme` / 演示 JWT 则拒绝启动；本地需显式 `ALLOW_INSECURE_DEFAULTS=true`。
- **第三方密钥不过浏览器**，只进服务端/BFF。
- demo 可用「单文件 secrets + apply」；prod 走 configure 随机化 + 轮换说明。
- 真实 `.env`、私钥、`build.secrets.env` 必须 gitignore。
