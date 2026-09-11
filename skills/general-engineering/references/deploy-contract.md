# ops / deploy 契约

把「装到机器上的目录」和「怎么编排发布」分开。搬脚本可以，搬安装路径会断交付。

## 分工

```text
deploy/<product>/          # 契约：目标机看到的布局
  configure.sh
  verify.sh
  upgrade.sh
  backup.sh
  rollback.sh              # 至少有说明或 stub + status
  docker-compose*.yml
  host.env.example

ops/deploy/                # 编排：pack、上传、调用远端
  build-package.sh
  release-remote.sh

# 根目录薄包装
./deploy-remote.sh → ops/deploy/release-remote.sh
```

无产品名时用 `deploy/app/`。

## 制品与环境

- 测试制品与生产制品分轨：标签、仓库、或至少文档规定「测试包禁止直接当生产包」。
- demo 线与 prod 线：密钥策略不同；compose overlay 优于一份巨型文件。
- 可观测性包可独立（L2）：不要「要监控必须重装业务」。

## verify / rollback

发布阶段最小意识：

- `verify`：健康、必要鉴权、关键配置已注入
- `rollback`：回到上一制品或文档化的手工步骤

bootstrap 可以先写脚本头 + README `status: planned`，但路径要占住。不要在文档宣称「已支持生产发布」。

## 离线包（可选）

`pack`（构建机）→ `install`/`upgrade`（目标机）。用户没提空气隔离就不要展开。
