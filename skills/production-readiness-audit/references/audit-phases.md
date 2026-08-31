# Audit Phases（Phase 0–20 详细检查项）

按顺序执行。发现高风险问题立即记录 P0/P1，不要等最终总结。

## Phase 0 — Establish Audit Scope

识别：项目类型、业务重要性、用户规模、数据敏感度、可用性要求、合规要求、部署环境、技术栈、当前开发模式。信息无法从仓库获得时标记 `UNKNOWN`，不要阻塞审计。

## Phase 1 — Repository Reconnaissance

扫描仓库结构（source / tests / docs / scripts / config / infrastructure / deployment / database / CI-CD，实际目录名不一定相同）。

识别：Frontend、Backend、Services、Libraries、Workers、Jobs、Database、Infrastructure。

识别架构形态：Monolith / Modular Monolith / Microservices / Serverless / Full-stack / Frontend-heavy / Backend-heavy / Event-driven / Hybrid。

输出内部 `Repository Map`。

## Phase 2 — Technology Inventory

识别：Language、Framework、Runtime、Database、Cache、Message Queue、Search、Object Storage、Authentication、Third-party APIs、Cloud、Container、CI/CD。

同时检查：Version、Dependency、Deprecated dependency、Known vulnerability、Unsupported runtime。

输出 `Technology Inventory`。

## Phase 3 — Architecture Reconstruction

不要完全相信 README。从代码反向推导实际调用链：

```text
User → Frontend → API → Application Service → Domain Logic → Repository → Database
```

以及 External Services / Message Queue / Cache / Storage / Authentication。

建立 `Actual Architecture`，与 `Documented Architecture` 比较；不一致则记录 `Architecture Documentation Drift`。

## Phase 4 — Critical Business Path

识别 Top 3~10 条关键业务链路（如 Login、Create Order、Payment、Approval、Data Import/Export、Report、User Management、Permission Management）。

对每条链路检查全链条：

```text
Input → Validation → Authorization → Business Logic → Transaction → Persistence
→ External Dependency → Response → Logging → Error Handling
```

## Phase 5 — Static Engineering Audit

- **Architecture**：Coupling、Cohesion、Dependency、Circular dependency
- **Code**：Complexity、Duplication、Dead code、Large files/functions、God objects、Magic values、Error handling
- **Security**：Auth、Permission、Input validation、Secrets
- **Reliability**：Timeout、Retry、Idempotency、Transaction、Concurrency

代码质量的核心判断标准：**一个没有参与项目开发的 Senior Engineer 能否理解并安全修改这些代码？**

## Phase 6 — Automated Verification

安全条件允许时执行：Install、Build、Lint、Type Check、Unit Test、Integration Test、E2E Test、Dependency Audit、Security Scan。

优先使用项目已有脚本（package.json、Makefile、Taskfile、pyproject.toml、pom.xml、build.gradle、go.mod），不要凭空创造命令。

命令失败时先分析 Command / Exit Code / Error / Root Cause / Impact，区分：Project Failure、Environment Failure、Missing Dependency、Configuration Failure、Test Failure。

## Phase 7 — Testing Audit

建立 `Critical Flow × Test Type` 矩阵：

| Business Flow | Unit | Integration | E2E | Failure Path |
| --- | --- | --- | --- | --- |

重点检查失败路径覆盖：Happy Path、Validation Failure、Authorization Failure、Database Failure、Network Failure、Timeout、Retry、Duplicate Request、Concurrent Request、Third-party Failure。

重点不是 Code Coverage，而是：**测试是否能真正阻止高风险 Bug 进入生产环境？**

## Phase 8 — Security Audit

审计路径：Attack Surface → Authentication → Authorization → Input → Business Logic → Data → Dependencies → Infrastructure。

检查面：Authentication、Authorization、RBAC/ABAC、Session management、Token handling、Input validation、Security headers、CORS、Rate limiting、Audit logging、Secret management、Dependency vulnerabilities。

特别检查：IDOR、Privilege Escalation、Broken Access Control、SQL Injection、XSS、SSRF、CSRF、Sensitive Data Exposure、Secret Leakage、Weak Session Management、Insecure File Upload。

发现高风险问题立即记录 P0/P1。

## Phase 9 — Database Audit

检查：Schema、Index、Query、Transaction、Isolation、Locking、Concurrency、Migration、Rollback、Consistency、Referential integrity、Soft delete、Audit fields、Backup、Restore、Data retention。

Migration Safety 必答：

1. 是否向前兼容？
2. 是否存在破坏性 Migration？
3. 是否支持 Rollback？
4. 是否需要停机？
5. 大表 Migration 是否可能锁表？
6. 是否可能丢失数据？

核心关注：**Database migration 是否可能导致生产数据不可逆损坏。**

## Phase 10 — CI/CD Audit

检查流水线：Commit → CI → Build → Test → Security Scan → Artifact → Deploy → Health Check → Release。

检查面：Build、Lint、Type check、Test、Security scan、Artifact、Versioning、Deployment、Environment separation、Approval、Rollback、Release strategy。

必答：**能否从一个 Git Commit 自动、可重复地得到一个可追踪的生产版本？**

## Phase 11 — Deployment Audit

检查：Environment separation、Config、Secrets、Health check、Readiness、Liveness、Resource limits、Scaling、Networking、Rollback。

必答：**如果刚发布的版本存在严重 Bug，能否在合理时间内恢复到上一个稳定版本？**

## Phase 12 — Observability Audit

检查：Logs、Metrics、Traces、Errors、Alerts、Dashboards（含 SLI / SLO / Error budget / Business metrics）。

针对关键业务链路回答：Can we detect? Can we alert? Can we diagnose? Can we mitigate? Can we recover?

总判断：**如果生产环境现在发生 P1 事故，团队能否在 30 分钟内知道哪里坏了、为什么坏、影响多大、如何止损？**

## Phase 13 — Failure Simulation

逐一推演以下故障场景：

1. Database unavailable
2. Cache unavailable
3. Third-party API timeout
4. Third-party API returns invalid data
5. Application instance crashes
6. Bad deployment
7. Database migration failure
8. Traffic spike
9. Dependency service unavailable
10. Duplicate request / retry storm

每个 Scenario 输出：Detection / Alert / Diagnosis / Mitigation / Recovery / Rollback / Risk。

## Phase 14 — Vibe Engineering Audit

读 `vibe-engineering.md` 执行 AI Coding 工程债务专项审计。

## Phase 15 — Maintainability Test

模拟一个新工程师加入项目，尝试回答：

```text
Where does authentication happen?
Where is authorization enforced?
Where is business logic located?
Where does database access happen?
Where are transactions defined?
How are errors handled?
How is configuration loaded?
How are secrets managed?
How is deployment performed?
How is rollback performed?
How is monitoring performed?
How do I safely add a new feature?
```

无法回答的项记录为 `Maintainability Risk`。

## Phase 16 — Engineering Governance Audit

检查：Branch strategy、Code review、Ownership、CODEOWNERS、Architecture Decision Records、API contract、Coding conventions、Dependency policy、Release process、Incident process、Documentation、Technical debt management。

## Phase 17 — Score

每个维度输出 `Score: 0~10` + `Confidence: HIGH/MEDIUM/LOW/UNKNOWN`，并解释 Evidence / Strength / Weakness / Risk / Recommendation。权重见 SKILL.md，打分必须对照 `report-templates.md` 的 Scoring Rubric 锚点。

## Phase 18 — Production Gate

输出 GO / CONDITIONAL GO / NO-GO，必须说明 Why、Production Blockers、Residual Risks、Required Actions。判定细则见 `report-templates.md`。

## Phase 19 — Remediation Roadmap

问题分组：Before Production / First 7 Days / First 30 Days / First 90 Days，按 Impact / Effort / Priority 排序。

## Phase 20 — Generate Audit Artifacts

环境允许创建文件时，在 `.audit/` 目录下生成审计产物（清单与模板见 `report-templates.md`）。这些文件属于 Audit Artifacts，不得触碰业务代码。
