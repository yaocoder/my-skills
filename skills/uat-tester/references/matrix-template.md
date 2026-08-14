# UAT 用例追溯矩阵模板

> 直接复制本文件到被测项目的 `docs/uat/matrix.md`，按实际填充。生成工具：`scripts/gen-matrix.py`。

---

## 1. 角色矩阵

| 角色 | 编号 | 可见菜单 | 数据范围 | 关键写权限 | 不可见/无权直达 |
|---|---|---|---|---|---|
| 超级管理员 | ROLE_ADMIN | 全部 | ALL | 全部 | — |
| 业务运营 | ROLE_OPS | 运营/门店/告警 | ALL | 订单/告警处理 | 系统/设备 |
| 区域经理 | ROLE_REGION | 运营/门店/告警 | ORG(本区及下级) | 订单 | 系统/设备 |
| 督导 | ROLE_SUPERVISOR | 运营/告警 | ORG(本组织) | 订单验收/名单申报 | 门店管理/系统/设备 |
| 店长 | ROLE_STORE_MGR | 告警/运营/经营 | STORE(本店) | 名单申报 | 门店管理/系统/设备 |
| 安全员 | ROLE_SECURITY | 安全中心 | ALL | 告警处理/名单审批 | 门店/系统/设备 |
| IT 管理员 | ROLE_IT | 系统/设备 | ALL | 用户/角色/设备 | 业务模块 |
| 禁用账号 | (disabled) | — | — | — | 全部（登录即拒） |

> 数据范围枚举：ALL=全量 / ORG=本组织及下级 / STORE=本店 / SELF=本人。详见 `roles-data-scope.md`。

## 2. 验收清单

> 编号 `<域>-<序号>`，域前缀按模块：G=通用/登录、DASH=驾驶舱、STORE=门店、SEC=安全、OPS=运营、BIZ=经营、DEV=设备、SYS=系统、V=视频、M=移动端...

| 验收项 | 优先级 | 说明 |
|---|---|---|
| AUTH-01 | P0 | 登录页可访问、表单齐全 |
| AUTH-02 | P0 | 正确账号密码登录成功 |
| AUTH-03 | P0 | 错误密码登录失败 |
| AUTH-04 | P0 | 禁用账号登录被拒 |
| AUTH-05 | P0 | 未登录访问受保护页 → 跳登录 |
| AUTH-06 | P0 | 登录后按权限落地页 |
| AUTH-07 | P0 | 登出返回登录页 |
| MENU-01 | P0 | 各角色菜单可见性按矩阵 |
| MENU-02 | P0 | 无权直达 URL 被守卫拦截 |
| DASH-01 | P0 | 驾驶舱首屏渲染 |
| DASH-02 | P0 | 范围条显示数据范围 |
| ... | | |

## 3. 用例追溯矩阵

> 用例编号 `UAT-<组>-<n>`；状态：✅ 已覆盖 / 🅿️ P0本批 / ⏳ 二期 / ❌ 不测

### 3.1 通用与登录

| 验收项 | 优先级 | 用例 | 状态 | 实现文件 |
|---|---|---|---|---|
| AUTH-01 | P0 | UAT-AUTH-01 登录页渲染与必填校验 | ✅ | auth.spec.ts |
| AUTH-02 | P0 | UAT-AUTH-02 各角色登录成功 | ✅ | auth.spec.ts / globalSetup |
| AUTH-03 | P0 | UAT-AUTH-03 错误密码提示 | ✅ | auth.spec.ts |
| AUTH-04 | P0 | UAT-AUTH-04 禁用账号被拒 | ✅ | auth.spec.ts |
| AUTH-05 | P0 | UAT-AUTH-05 未登录守卫 | ✅ | auth.spec.ts |
| AUTH-06 | P0 | UAT-AUTH-06 各角色落地页 | ✅ | auth.spec.ts |
| AUTH-07 | P0 | UAT-AUTH-07 登出 | ✅ | auth.spec.ts |

### 3.2 角色权限专项（重点）

| 角色 | 断言点 | 用例 | 状态 | 实现文件 |
|---|---|---|---|---|
| 督导 | 菜单可见性 / 数据范围 / 可验收 / 名单申报可写 / 定级规则写=403 / 无权直达拦截 / **落地页零噪音 / 深链接抽屉覆盖** | UAT-RBAC-SUP-01~08 | ✅ | rbac-supervisor.spec.ts |
| 店长 | 菜单可见性 / 数据范围SELF / 工单只读 / 名单申报 / 定级规则写=403 / 无权直达 / **落地页零噪音** | UAT-RBAC-MGR-01~06 | ✅ | rbac-store-manager.spec.ts |

### 3.3 状态流转专项

| 场景 | 状态链 | 用例 | 状态 | 实现文件 |
|---|---|---|---|---|
| 手工创建 → 列表可见 | PENDING | UAT-WO-01 | ✅ | workorder-flow.spec.ts |
| 处理中 → 待验收 | PENDING→PROCESSING→WAITING_VERIFY | UAT-WO-02 | ✅ | workorder-flow.spec.ts |
| 验收通过 | WAITING_VERIFY→CLOSED | UAT-WO-03 | ✅ | workorder-flow.spec.ts |
| 验收驳回 | WAITING_VERIFY→REJECTED | UAT-WO-04 | ✅ | workorder-flow.spec.ts |
| 角色视角差异 | 可验收 vs 只读 | UAT-WO-05 | ✅ | workorder-flow.spec.ts |

### 3.4 用户旅程

| 剧本 | 用户 | 旅程 | 用例 | 状态 |
|---|---|---|---|---|
| A 全流程 | admin | 登录→驾驶舱→门店→告警→工单→系统 | UAT-JOURNEY-01 | ✅ |
| B 安全员 | security | 登录→告警处理→派单→名单申报 | UAT-JOURNEY-02 | ✅ |
| C 区域 | region | 登录→驾驶舱(范围)→门店(范围)→告警(范围) | UAT-JOURNEY-03 | ✅ |
| D 店长 | mgr | 登录→告警(本店)→工单(只读)→名单申报 | UAT-JOURNEY-04 | ✅ |

## 4. 四原则落地清单

| 角色/模块 | 零噪音用例 | 深链接入口 | 数据范围断言 | 幂等造数 |
|---|---|---|---|---|
| 督导 | UAT-RBAC-SUP-07 落地页零403 | UAT-RBAC-SUP-08 巡店报告抽屉 | UAT-RBAC-SUP-02 华东范围 | ensureWorkOrder/ensureWatchlist |
| 店长 | UAT-RBAC-MGR-05 落地页零403 | UAT-RBAC-MGR-06 工单详情只读 | UAT-RBAC-MGR-02 本店SELF | ensureWorkOrder |
| 区域 | UAT-RBAC-REG-xx | 订单详情 | 本区可见/异区不可见 | ensureOrder |
| ... | | | | |

## 5. 不测范围（明确排除）

- 移动端原生（本期不测的端）
- WebSocket 实时推送的 UI 呈现（状态流转以 API/页面结果为准）
- 真实地图/视频流播放（无真实 Key，断降级占位）
- 真实第三方支付/短信（不触发）
- 改密/删账号等破坏性操作（会破坏后续用例）
