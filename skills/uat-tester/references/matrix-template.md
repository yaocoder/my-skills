# UAT 用例追溯矩阵模板

> 直接复制本文件到被测项目的 `docs/uat/matrix.md`，按实际填充。生成工具：`scripts/gen-matrix.py`。

---

## 1. 角色矩阵

| 角色 | 编号 | 可见菜单 | 数据范围 | 关键写权限 | 不可见/无权直达 |
|---|---|---|---|---|---|
| 超级管理员 | ROLE_ADMIN | 全部 | ALL | 全部 | — |
| 业务管理员 | ROLE_MANAGER | 工作台/资源管理/报表 | ALL | 资源管理/报表 | 系统设置 |
| 编辑者 | ROLE_EDITOR | 工作台/资源管理 | ORG | 资源增删改 | 报表/系统设置 |
| 审核者 | ROLE_REVIEWER | 工作台/资源管理/报表 | DEPT | 资源审核 | 系统设置 |
| 普通用户 | ROLE_USER | 工作台/个人中心 | SELF | 个人信息 | 资源管理/报表/系统设置 |
| 禁用账号 | (disabled) | — | — | — | 全部（登录即拒） |

> 数据范围枚举：ALL=全量 / ORG=本组织及下级 / DEPT=本部门 / SELF=本人。详见 `roles-data-scope.md`。

## 2. 验收清单

> 编号 `<域>-<序号>`，域前缀按模块：AUTH=认证/登录、MENU=菜单/权限、DASH=工作台、RES=资源管理、FLOW=状态流转...

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
| DASH-01 | P0 | 工作台首屏渲染 |
| DASH-02 | P0 | 工作台数据按权限范围展示 |
| RES-01 | P0 | 资源列表分页查询 |
| RES-02 | P0 | 资源新增/编辑/删除 |
| FLOW-01 | P0 | 资源状态流转：草稿→待审核 |
| FLOW-02 | P0 | 审核通过：待审核→已发布 |
| FLOW-03 | P0 | 审核驳回：待审核→已驳回 |
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
| 编辑者 | 菜单可见性 / 数据范围ORG / 资源增删改可写 / 审核入口=403 / 无权直达拦截 / **落地页零噪音 / 深链接抽屉覆盖** | UAT-RBAC-EDITOR-01~08 | ✅ | rbac-editor.spec.ts |
| 普通用户 | 菜单可见性 / 数据范围SELF / 资源只读 / 编辑操作=403 / 无权直达 / **落地页零噪音** | UAT-RBAC-USER-01~06 | ✅ | rbac-user.spec.ts |

### 3.3 状态流转专项

| 场景 | 状态链 | 用例 | 状态 | 实现文件 |
|---|---|---|---|---|
| 手工创建 → 列表可见 | DRAFT | UAT-FLOW-01 | ✅ | resource-flow.spec.ts |
| 提交审核 | DRAFT→PENDING_REVIEW | UAT-FLOW-02 | ✅ | resource-flow.spec.ts |
| 审核通过 | PENDING_REVIEW→PUBLISHED | UAT-FLOW-03 | ✅ | resource-flow.spec.ts |
| 审核驳回 | PENDING_REVIEW→REJECTED | UAT-FLOW-04 | ✅ | resource-flow.spec.ts |
| 角色视角差异 | 可编辑 vs 只读 | UAT-FLOW-05 | ✅ | resource-flow.spec.ts |

### 3.4 用户旅程

| 剧本 | 用户 | 旅程 | 用例 | 状态 |
|---|---|---|---|---|
| A 管理员全流程 | admin | 登录→工作台→资源管理→创建资源→系统设置 | UAT-JOURNEY-01 | ✅ |
| B 编辑→审核 | editor | 登录→工作台→创建资源→提交审核 | UAT-JOURNEY-02 | ✅ |
| C 审核者审批 | reviewer | 登录→工作台→待审核列表→审批通过/驳回 | UAT-JOURNEY-03 | ✅ |
| D 普通用户 | user | 登录→工作台→查看资源→个人中心 | UAT-JOURNEY-04 | ✅ |

## 4. 四原则落地清单

| 角色/模块 | 零噪音用例 | 深链接入口 | 数据范围断言 | 幂等造数 |
|---|---|---|---|---|
| 编辑者 | UAT-RBAC-EDITOR-07 落地页零403 | UAT-RBAC-EDITOR-08 资源编辑抽屉 | UAT-RBAC-EDITOR-02 本组织范围 | ensureResource |
| 普通用户 | UAT-RBAC-USER-05 落地页零403 | UAT-RBAC-USER-06 资源详情只读 | UAT-RBAC-USER-02 本人SELF | ensureResource |
| 审核者 | UAT-RBAC-REVIEWER-xx | 审核详情页 | 本部门可见/异部门不可见 | ensureResource |
| ... | | | | |

## 5. 不测范围（明确排除）

- 移动端原生（本期不测的端）
- WebSocket 实时推送的 UI 呈现（状态流转以 API/页面结果为准）
- 真实地图/视频流播放（无真实 Key，断降级占位）
- 真实第三方支付/短信（不触发）
- 改密/删账号等破坏性操作（会破坏后续用例）