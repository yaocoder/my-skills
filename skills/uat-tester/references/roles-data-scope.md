# 角色矩阵与数据范围断言模板

> 角色矩阵是 UAT 体系的骨架。设计不对，后面所有用例都会偏。

---

## 1. 角色矩阵设计法

### 1.1 提取角色的三个维度

对每个角色，明确：

1. **菜单可见性**：可见哪些菜单组、不可见哪些、无权直达哪些 URL（被路由守卫拦回）。
2. **数据范围策略**：见 §2 枚举。
3. **写权限差异**：能创建/编辑/删除/审批哪些实体；哪些写接口对它是 403。

### 1.2 矩阵表（复制填充）

| 角色 | 可见菜单 | 数据范围 | 可写操作 | 不可见/无权直达 | 写=403 的接口 |
|---|---|---|---|---|---|
| 超管 | 全部 | ALL | 全部 | — | — |
| 运营 | 运营/门店/告警 | ALL | 订单CRUD/告警处理 | 系统/设备 | 系统设置 |
| 区域 | 运营/门店/告警 | ORG(本区及下级) | 订单 | 系统/设备 | 跨区订单 |
| 督导 | 运营/告警 | ORG(本组织) | 订单验收/名单申报 | 门店管理/系统/设备 | 订单删除/系统 |
| 店长 | 告警/运营/经营 | STORE(本店) | 名单申报 | 门店管理/系统/设备 | 订单验收/删除 |
| 安全员 | 安全中心 | ALL | 告警处理/名单审批 | 门店/系统/设备 | 订单 |
| IT | 系统/设备 | ALL | 用户/角色/设备 | 业务模块 | 订单/告警 |
| 禁用 | — | — | — | 全部 | — |

### 1.3 验证矩阵完整性的 checklist

- [ ] 每个角色至少 1 条「菜单可见性按矩阵」用例（断言可见 + 不可见 = 0）
- [ ] 每个角色至少 1 条「无权直达 URL 被守卫拦回」用例
- [ ] 每个角色至少 1 条「落地页零噪音」用例（§4.1）
- [ ] 每个角色至少 1 条「深链接/抽屉覆盖」用例（§4.2）
- [ ] 涉及列表的角色至少 1 条「数据范围」用例（§4.3，两个范围数据点）
- [ ] 每个角色至少 1 条「403 双轨」用例（UI 无按钮 + API 直调 403）

---

## 2. 数据范围策略枚举

| 策略 | 含义 | 典型角色 | 断言方式 |
|---|---|---|---|
| ALL | 全量数据 | 超管/安全员（全局） | 任意数据可见 |
| ORG | 本组织及下级 | 区域经理/督导 | 本组织数据可见，异组织不可见 |
| STORE | 本店 | 店长 | 本店数据可见，他店不可见 |
| SELF | 本人 | 普通用户（自己的订单） | 仅自己的数据可见 |

### 2.1 复合范围

有些系统支持复合：`ORG + STORE`（本组织内 + 额外授权的门店）。矩阵里注明复合规则。

### 2.2 容易漏的越权点

- **导出**：列表不可见 ≠ 导出不可见。导出必须单独断言内容不含异区数据。
- **搜索/筛选**：异区数据不应出现在搜索结果。
- **详情直链**：直接访问 `/orders/<异区id>` 应被守卫拦截（403 或重定向），而非 200 显示。
- **API 层**：UI 看不到 ≠ API 拿不到。角色 token 直调列表/详情接口，断言返回数据在范围内。

---

## 3. 数据范围断言模板（框架无关伪代码）

### 3.1 列表可见性

```
预置：
  world.storeId = 本店A
  world.otherStoreId = 异店B
  ensureOrder(opsToken, { title: "UAT-本店-"+ts, storeId: world.storeId })
  ensureOrder(opsToken, { title: "UAT-异店-"+ts, storeId: world.otherStoreId })

断言（店长视角，STORE 范围）：
  page.goto("/orders")
  expect(page.getByText("UAT-本店-")).toBeVisible()
  expect(page.getByText("UAT-异店-")).toHaveCount(0)
```

### 3.2 详情直链守卫

```
预置异店订单 id

断言（店长视角）：
  page.goto("/orders/<异店id>")
  expect(page).not.toHaveURL(/\/orders\//)   # 被拦回落地页
  # 或 API 层：
  res = fetch(`${bff}/api/orders/<异店id>`, { headers: { Authorization: `Bearer ${mgrToken}` } })
  expect(res.status).toBe(403)
```

### 3.3 导出内容

```
预置本店 + 异店订单

断言（店长视角）：
  page.goto("/orders")
  page.getByTestId("export-button").click()
  content = await downloadContent()
  expect(content).toContain("UAT-本店-")
  expect(content).not.toContain("UAT-异店-")
```

### 3.4 API 层数据范围兜底

```
res = fetch(`${bff}/api/orders/list`, {
  method: "POST",
  headers: { Authorization: `Bearer ${mgrToken}` },
  body: JSON.stringify({ page: 1, pageSize: 100 })
})
data = await res.json()
storeIds = data.list.map(o => o.storeId)
expect(storeIds.every(id => id === world.storeId)).toBe(true)   # 全部是本店
```

---

## 4. 角色账号预置约定

### 4.1 命名

统一 `uat.<role>` 命名（如 `uat.supervisor`、`uat.mgr`），便于 globalSetup 幂等预置。

### 4.2 密码

统一测试密码，走环境变量 `E2E_TEST_PASS`，**勿提交真实密钥**。

### 4.3 禁用账号

预置一个 `uat.disabled` 账号（status=disabled），用于登录失败用例。

### 4.4 数据范围绑定

预置时把数据范围绑定到角色：
- ORG 角色：`dataScopeOrgIds = [eastOrgId]`
- STORE 角色：`storeId = eastStoreId`

这样后端的数据范围过滤才能生效，E2E 断言才有意义。

---

## 5. 403 断言双轨（UI + API）

权限断言必须双轨，缺一不可：

### 5.1 UI 层

```
page.goto("/orders/<id>")
expect(page.getByTestId("order-delete-button")).toHaveCount(0)   # 无删除按钮
expect(page.getByTestId("order-verify-pass")).toHaveCount(0)      # 督导可见但店长不可见
```

### 5.2 API 层

```
res = fetch(`${bff}/api/orders/<id>/delete`, {
  method: "DELETE",
  headers: { Authorization: `Bearer ${roleToken}` }
})
expect(res.status).toBe(403)
```

**为什么双轨**：UI 层只断「按钮不存在」——但前端可能漏了隐藏按钮（bug），后端 403 才是真正的权限防线。反过来，只断 API 403 也不够——前端可能错误地显示了按钮（点下去才 403，体验差）。两层都断，才能锁定「既不显示又调不通」。
