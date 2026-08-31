# Vibe Engineering Audit（AI Coding 工程债务专项）

传统 Code Review 容易漏掉的问题恰恰是本专项的核心：AI 在持续生成局部最优解的过程中，系统整体架构正在发生漂移。单看每一段代码都「看起来有道理」，但系统级视角下问题链是：

`Duplication → Inconsistency → Drift → Temporary Fix → Hidden Complexity → Knowledge Dependency`

## 检查清单

### 1. Code Duplication

检查是否存在：同一业务逻辑多份实现、相似 API、相似 Service、相似 Validation、相似 Permission Check、相似 Error Handling。

典型信号（每个文件单看都合理，合起来就是漂移）：

```text
OrderService.ts
OrderServiceV2.ts
OrderBusinessService.ts
OrderHelper.ts
OrderUtils.ts
OrderProcessor.ts
```

### 2. Architecture Drift

检查：模块边界不断扩大、Service 职责不断膨胀、Controller 直接操作数据库、UI 层包含业务逻辑、Domain Logic 散落、Utility 变成「万能工具箱」。

### 3. AI Patch Accumulation

寻找：临时 workaround、TODO、FIXME、Hack、Compatibility code、Dead code、Unused abstraction、Over-engineering、Premature abstraction。

大量 TODO/FIXME 暗示系统处于持续临时修复状态。

### 4. Inconsistent Patterns

检查是否存在多种并存的：API response 格式、错误处理方式、数据库访问方式、认证方式、日志方式、配置方式、状态管理方式。

### 5. Human Knowledge Dependency

判断：**项目是否已经变成「只有原作者 + AI 上下文才能维护」的系统？**

如果项目必须依赖原作者记忆、某个 Agent 的上下文、某几个 Prompt、某个开发者脑中的架构、一堆「你问 AI 它才能告诉你」的隐性知识，那么它实际上还没有真正工程化。

## 典型 Pattern（逐一排查）

- **Pattern A**：同一个业务规则存在多个实现。
- **Pattern B**：多个 AI Agent / Developer 使用了不同实现方式。
- **Pattern C**：同一类问题存在多个错误处理模式。
- **Pattern D**：Service / Utility / Helper 不断膨胀。
- **Pattern E**：代码能运行，但没人能解释为什么这么设计。
- **Pattern F**：README 与真实代码明显不一致。
- **Pattern G**：大量 TODO/FIXME 暗示持续临时修复状态。

另需寻找：Hidden dependency、Prompt-context dependency、Missing tests、Missing documentation、Over-abstraction、Under-abstraction。

## 输出

必须输出总体评级并逐项分析：

```text
Vibe Engineering Risk: LOW / MEDIUM / HIGH / CRITICAL
```

分析维度：AI-generated duplication、Architecture drift、Hidden complexity、Temporary workaround、Missing tests、Missing documentation、Knowledge dependency、Governance gap。

## 评级立场

AI Coding 本身不是风险，不要因为项目用了 AI 就压低分数。要评价的是 AI Coding 是否被工程体系有效约束（测试、静态分析、安全检查、CI/CD、可观测性、持续改进闭环）。有闭环 ≠ 低成熟度；`Prompt → Generate → Looks Good → Ship` 才是高风险。
