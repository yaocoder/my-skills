# 报告模板与审计产物

## Scoring Rubric（评分锚点）

每个维度 0~10 打分时对照以下锚点，取最接近的档位再微调 ±1。目的：让同一项目多次评分、不同模型评分结果收敛。

| 档位 | 通用标准 |
| --- | --- |
| 0~2 | 该维度基本不存在。无任何可验证证据，或存在会直接导致生产事故的根本性缺失（如完全没有测试、Secret 明文提交、无任何部署方式） |
| 3~4 | 有零星实践但不成体系。局部存在、覆盖关键业务不足一半、依赖手工操作、无法阻止高风险变更进入生产 |
| 5~6 | 基本体系成型但有明显缺口。关键业务大部分覆盖，失败路径/边界场景缺失，出问题时能应对但靠人肉 |
| 7~8 | 体系完整、自动化为主。关键业务全覆盖含失败路径，有可重复流程和回退手段，缺口仅在次要区域 |
| 9~10 | 企业级标杆。全面自动化、可验证、可演练，有度量与持续改进证据（如 SLO、演练记录、债务看板） |

打分纪律：

- 锚点判断基于 Evidence，无证据的能力不计入正面得分（Never Assume 同样适用于打分）。
- Confidence 为 LOW/UNKNOWN 的维度，分数向下取整并在报告中注明。
- 禁止「感觉不错给 7 分」——每个分数必须能指出对应锚点行 + 支撑证据。

## 报告裁剪规则

报告规模与项目规模、审计模式匹配。核心原则：**空表格不如不填**，篇幅留给真正的风险。

- **Quick Audit**：不使用 17 节模板。只输出：Executive Summary、Critical Findings（P0/P1）、Production Blockers、简版 Final Verdict、是否建议升级 Full Audit。
- **专项模式**（security/architecture/testing/vibe）：只输出 Executive Summary + 对应 Assessment 节 + Critical Findings + 该专项的 Verdict。
- **小型项目**（单服务、无独立基础设施、团队 ≤3 人）：Full Audit 报告缩至 6~8 节——保留 1/3/4/5/15/17，其余节只在有实质发现时保留。Infrastructure、Failure Simulation 等不适用的节写一行「N/A + 原因」即可。
- **中大型项目 Full Audit**：使用完整 17 节，但任何小节若无实质发现，用一句话说明后跳过，不生成空表格。
- `.audit/` 产物同理：只生成有内容的文件，README.md 中注明省略了哪些及原因。

## Production Gate 判定细则

### GO（必须全部满足）

- 无 P0
- 无未解决关键 P1
- 核心业务有有效测试
- 生产配置明确
- Secret 管理可靠
- 数据库具备迁移方案
- 有备份与恢复策略
- 有部署机制、有 Rollback
- 有日志、监控、告警
- 核心故障具有恢复路径

### CONDITIONAL GO

- 无 P0
- P1 风险可接受
- 已明确风险 Owner
- 已制定修复计划
- 已知风险不会直接破坏核心业务

### NO-GO（出现任意一项）

- P0
- 严重安全漏洞
- 数据一致性重大问题
- 无法恢复核心数据
- 无法可靠部署 / 无法回滚关键版本
- 核心业务完全没有验证
- 关键生产能力完全未知

注意：总分高不代表能上线。例如 Code Quality 9/10、Testing 8/10，但 Production Secret 明文存在 Git，依然 NO-GO。

---

## 最终报告结构（17 节，严格套用）

### 1. Executive Summary

不超过 10 条，必须包含：Overall Score、Maturity Level、Production Gate、P0 Count、P1 Count、Biggest Risk、Biggest Strength、Top 3 Actions。

### 2. Project Profile

| Item | Value |
| --- | --- |
| Project Type |  |
| Business Criticality |  |
| Technology Stack |  |
| Deployment |  |
| Data Sensitivity |  |
| Expected Scale |  |
| AI Coding Usage |  |
| Overall Risk |  |

### 3. Engineering Maturity

| Dimension | Score | Weight | Confidence |
| --- | --- | --- | --- |
| Architecture |  | 12% |  |
| Code Quality |  | 10% |  |
| Testing |  | 15% |  |
| Security |  | 15% |  |
| CI/CD |  | 10% |  |
| Infrastructure |  | 10% |  |
| Database |  | 10% |  |
| Observability |  | 10% |  |
| Documentation |  | 4% |  |
| Governance |  | 4% |  |

```text
Overall Score: XX/100
Maturity Level: Level X
```

### 4. Production Gate

只允许 GO / CONDITIONAL GO / NO-GO，并说明原因。

### 5. Critical Findings

| ID | Severity | Area | Finding | Evidence | Impact | Action |
| --- | --- | --- | --- | --- | --- | --- |

按 P0 → P1 → P2 → P3 排序。

### 6. Architecture Assessment

Actual Architecture、Strengths、Weaknesses、Architecture Drift、Technical Debt、Recommended Actions。

### 7. Code Quality Assessment

Maintainability、Complexity、Duplication、Coupling、Error Handling、Type Safety、Dependency Management。

### 8. Testing Assessment

Test Strategy、Test Coverage、Critical Business Coverage、Failure-path Coverage、Regression Protection、Testing Gaps。

必答：当前测试是否足以支持安全发布？

### 9. Security Assessment

Authentication、Authorization、Input Validation、Data Security、Secret Management、Dependency Security、Infrastructure Security。

### 10. Production Readiness

| Capability | Status | Evidence | Risk |
| --- | --- | --- | --- |
| Build |  |  |  |
| CI |  |  |  |
| CD |  |  |  |
| Configuration |  |  |  |
| Secrets |  |  |  |
| Migration |  |  |  |
| Deployment |  |  |  |
| Rollback |  |  |  |
| Logging |  |  |  |
| Monitoring |  |  |  |
| Alerting |  |  |  |
| Backup |  |  |  |
| Recovery |  |  |  |

Status 只能使用：PASS / PARTIAL / FAIL / UNKNOWN。

### 11. Failure Simulation

| Scenario | Detection | Alert | Diagnosis | Recovery | Risk |
| --- | --- | --- | --- | --- | --- |

### 12. Vibe Engineering Risk

```text
Vibe Engineering Risk: LOW / MEDIUM / HIGH / CRITICAL
```

并分析：AI-generated duplication、Architecture drift、Hidden complexity、Temporary workaround、Missing tests、Missing documentation、Knowledge dependency、Governance gap。

### 13. Top 10 Risks

| Rank | Risk | Severity | Probability | Impact | Priority |
| --- | --- | --- | --- | --- | --- |

### 14. Production Blockers

只列真正阻止上线的问题。没有则输出：`No Production Blockers Identified`。

### 15. Remediation Roadmap

分四组：Before Production / First 7 Days / First 30 Days / First 90 Days。

### 16. New Engineer Takeover Test

必答：如果一个没有参与项目开发的 Senior Engineer 明天接手，他能否在 1~3 天内完成一次普通需求开发、测试和发布？

输出 `PASS / PARTIAL / FAIL` 并说明原因。

### 17. Final Verdict

```text
Engineering Maturity: XX/100

Maturity Level:
Level X — XXXXX

Production Readiness:
GO / CONDITIONAL GO / NO-GO

Vibe Engineering Risk:
LOW / MEDIUM / HIGH / CRITICAL

P0: X
P1: X
P2: X
P3: X
```

然后回答五问：

- Q1. 现在能不能上线？
- Q2. 最大的三个生产风险是什么？
- Q3. 上线前必须做什么？
- Q4. 上线后最应该优先治理什么？
- Q5. 如果继续使用 Vibe Engineering，未来 6~12 个月最大的工程风险是什么？

---

## `.audit/` 审计产物清单

环境允许写文件时生成（这些是 Audit Artifacts，不得修改业务代码；无法写入时直接在对话中输出报告）：

```text
.audit/
├── README.md                    # 产物索引与审计元信息（日期、模式、范围）
├── executive-summary.md         # 第 1 节
├── repository-map.md            # Phase 1 产出
├── architecture-assessment.md   # 第 6 节
├── security-assessment.md       # 第 9 节
├── testing-assessment.md        # 第 8 节
├── reliability-assessment.md    # Failure Simulation + Observability
├── production-readiness.md      # 第 10 节 + Production Gate
├── vibe-engineering-risk.md     # 第 12 节
├── findings.md                  # 第 5 节完整清单
├── remediation-plan.md          # 第 15 节
└── evidence-index.md            # 全部 Evidence 汇总（file:line、命令与结果）
```
