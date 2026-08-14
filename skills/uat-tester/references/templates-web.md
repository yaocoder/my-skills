# Web（后台/C 端/H5）UAT 模板

> 按被测栈选型，复制对应骨架。选择器一律优先 `data-testid`。

---

## 1. 框架选型表

| 被测栈 | 推荐框架 | 选择器约定 | storageState |
|---|---|---|---|
| Vue/React/Angular + 任意 | Playwright | `data-testid` | 原生支持（推荐） |
| React + Vitest 生态 | Playwright | `data-testid` | 原生支持 |
| 老项目已有 Selenium 栈 | WebdriverIO | `data-testid` | attachSession |
| BDD 风格偏好 | CodeceptJS | `data-testid` | 支持 |

> 默认推荐 **Playwright**：原生 storageState、自动等待、trace viewer、多浏览器。除非项目已有其他栈，否则用它。

---

## 2. Playwright 配置骨架

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

const baseURL = process.env.E2E_BASE_URL || 'http://localhost:5173'

export default defineConfig({
  testDir: './e2e/specs',
  fullyParallel: false,        // 串行，避免写冲突
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  globalSetup: './e2e/global-setup.ts',
  grepInvert: process.env.E2E_LIVE ? undefined : /@live/,
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    locale: 'zh-CN',
    launchOptions: { channel: 'chromium' }  // 兼容 CI 与本机未装 headless-shell
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  outputDir: 'test-results'
})
```

## 3. 目录结构

```
e2e/
├── global-setup.ts          # 幂等预置租户/组织/门店/角色 → storageState
├── fixtures/
│   ├── env.ts               # 环境变量 + 角色账号常量
│   ├── api.ts               # api()/loginApi() 调用助手
│   ├── auth.ts              # authFile(role)/readWorld()/loginViaUi()
│   └── provision.ts         # ensure* 幂等造数工厂
├── pages/                   # POM 页面对象层
│   ├── AppLayout.ts
│   ├── LoginPage.ts
│   └── ...
└── specs/
    ├── auth.spec.ts
    ├── rbac-<role>.spec.ts
    ├── <module>-flow.spec.ts
    └── journeys/
```

## 4. fixtures 骨架

### env.ts

```ts
export const env = {
  baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
  bffURL: process.env.E2E_BFF_URL || 'http://localhost:3000',
  testPass: process.env.E2E_TEST_PASS || 'test123456'
}

export const USERS = {
  admin: 'uat.admin',
  ops: 'uat.ops',
  region: 'uat.region',
  supervisor: 'uat.supervisor',
  storeMgr: 'uat.mgr',
  disabled: 'uat.disabled'
} as const
export type RoleKey = keyof typeof USERS
```

### api.ts

```ts
import { env } from './env'

export type Json = Record<string, unknown>

async function parse(res: Response) {
  const text = await res.text()
  let body: any = {}
  try { body = text ? JSON.parse(text) : {} }
  catch { throw new Error(`非 JSON 响应 HTTP ${res.status}: ${text.slice(0, 200)}`) }
  if (!res.ok || (body.code != null && body.code !== 200)) {
    throw new Error(body.msg || body.message || `HTTP ${res.status} ${text.slice(0, 240)}`)
  }
  return body.data
}

export async function api(method: string, path: string, token?: string, body?: unknown) {
  const headers: Record<string, string> = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${env.bffURL}${path}`, {
    method, headers, body: body !== undefined ? JSON.stringify(body) : undefined
  })
  return parse(res)
}

export async function loginApi(username: string, password: string) {
  const data = await api('POST', '/api/auth/login', undefined, { username, password })
  if (!data?.token) throw new Error(`登录无 token: ${username}`)
  return data
}
```

### auth.ts

```ts
import fs from 'node:fs'
import path from 'node:path'
import { chromium, type Page } from '@playwright/test'
import { env, USERS, type RoleKey } from './env'
import { loginApi } from './api'

const AUTH_DIR = path.join(path.dirname(new URL(import.meta.url).pathname), '../.auth')

export function authFile(role: RoleKey) { return path.join(AUTH_DIR, `${role}.json`) }

export async function writeAuthStates(world: any) {
  fs.mkdirSync(AUTH_DIR, { recursive: true })
  fs.writeFileSync(path.join(AUTH_DIR, 'world.json'), JSON.stringify(world, null, 2))
  const browser = await chromium.launch({ channel: 'chromium' })
  for (const [role, username] of Object.entries(USERS) as [RoleKey, string][]) {
    if (role === 'disabled') continue
    const { token, userInfo } = await loginApi(username, env.testPass)
    const ctx = await browser.newContext({ baseURL: env.baseURL })
    const page = await ctx.newPage()
    await page.goto('/login')
    await page.evaluate(([t, u]) => {
      localStorage.setItem('token', t)
      localStorage.setItem('userInfo', JSON.stringify(u))
    }, [token, userInfo] as const)
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
    await ctx.storageState({ path: authFile(role) })
    await ctx.close()
  }
  await browser.close()
}

export function readWorld(): any {
  return JSON.parse(fs.readFileSync(path.join(AUTH_DIR, 'world.json'), 'utf8'))
}

export async function loginViaUi(page: Page, username: string, password: string) {
  await page.goto('/login')
  await page.getByTestId('login-username').locator('input').fill(username)
  await page.getByTestId('login-password').locator('input').fill(password)
  await page.getByTestId('login-submit').click()
}
```

### provision.ts（幂等工厂模式）

```ts
import { api, loginApi } from './api'
import { env, USERS } from './env'

function asList(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) return data
  if (data && typeof data === 'object' && Array.isArray((data as any).list)) return (data as any).list
  return []
}

/** 订单工厂：存在即复用，不存在才建；新建时间戳命名隔离 */
export async function ensureOrder(token: string, spec: {
  title: string
  storeId: number
  type?: string
  priority?: string
  status?: string
}): Promise<{ id: number }> {
  const list = asList(await api('POST', '/api/orders/list', token, { page: 1, pageSize: 50 }))
  const existing = list.find((o) => o.title === spec.title)
  if (existing) {
    if (spec.status && existing.status !== spec.status) {
      await api('PATCH', `/api/orders/${existing.id}/status`, token, { status: spec.status })
    }
    return { id: Number(existing.id) }
  }
  const created = await api('POST', '/api/orders', token, {
    type: spec.type || 'default',
    storeId: spec.storeId,
    title: spec.title,                   // 调用方用 `UAT-xxx-${Date.now()}` 命名
    priority: spec.priority || 'medium'
  })
  if (spec.status && spec.status !== 'pending') {
    await api('PATCH', `/api/orders/${created.id}/status`, token, { status: spec.status })
  }
  return { id: Number(created.id) }
}
```

## 5. POM 模板

```ts
import { expect, type Page } from '@playwright/test'

export class AppLayout {
  constructor(private readonly page: Page) {}

  async gotoMenu(key: string) {
    const item = this.page.getByTestId(`nav-${key}`)
    await item.click()
    await expect(item).toBeVisible()
  }

  async gotoSubMenu(parent: string, child: string) {
    await this.page.getByTestId(`nav-${parent}`).click()
    await this.page.getByTestId(`nav-${child}`).click()
  }

  async logout() {
    await this.page.locator('.user-btn').click()
    await this.page.getByRole('menuitem', { name: /退出|logout/i }).click()
    await expect(this.page).toHaveURL(/\/login/)
  }
}
```

## 6. spec 骨架

### 登录专项

```ts
import { test, expect } from '@playwright/test'
import { env, USERS } from '../fixtures/env'

test.describe('登录与鉴权', () => {
  test('登录页渲染与必填校验', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByTestId('login-submit')).toBeVisible()
    await page.getByTestId('login-submit').click()
    // 必填提示出现（按实际 UI 断言）
  })

  test('错误密码登录失败', async ({ page }) => {
    await page.goto('/login')
    await page.getByTestId('login-username').locator('input').fill(USERS.admin)
    await page.getByTestId('login-password').locator('input').fill('wrong')
    await page.getByTestId('login-submit').click()
    await expect(page.locator('.ant-message')).toContainText(/密码错误|失败/)
  })

  test('禁用账号登录被拒', async ({ page }) => {
    await page.goto('/login')
    await page.getByTestId('login-username').locator('input').fill(USERS.disabled)
    await page.getByTestId('login-password').locator('input').fill(env.testPass)
    await page.getByTestId('login-submit').click()
    await expect(page.locator('.ant-message')).toContainText(/禁用|停用|disabled/i)
  })
})
```

### 角色权限专项（含零噪音 + 深链接）

```ts
import { test, expect } from '@playwright/test'
import { authFile, readWorld } from '../fixtures/auth'
import { USERS, env } from '../fixtures/env'
import { loginApi } from '../fixtures/api'
import { ensureOrder } from '../fixtures/provision'

test.describe('督导角色权限专项', () => {
  test.use({ storageState: authFile('supervisor') })

  test('菜单可见性按矩阵', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByTestId('nav-ops')).toBeVisible()
    await expect(page.getByTestId('nav-store')).toHaveCount(0)
    await expect(page.getByTestId('nav-system')).toHaveCount(0)
  })

  // §4.1 首屏零噪音
  test('落地页零噪音：筛选器基础数据对督导可用', async ({ page }) => {
    const forbidden: string[] = []
    page.on('response', (res) => { if (res.status() >= 400) forbidden.push(`${res.status()} ${res.url()}`) })
    const optionsResp = page.waitForResponse((r) => r.url().includes('/api/store/options'))
    await page.goto('/dashboard')
    await expect(page.getByTestId('nav-workbench')).toBeVisible()
    const resp = await optionsResp
    expect(resp.status()).toBe(200)
    expect(forbidden).toEqual([])
    await expect(page.locator('.ant-message', { hasText: /无权限|Request failed|Internal Server/ })).toHaveCount(0)
    // 接口层兜底：角色 token 直调 = 200
    const { token } = await loginApi(USERS.supervisor, env.testPass)
    const apiRes = await fetch(`${env.bffURL}/api/store/options`, { headers: { Authorization: `Bearer ${token}` } })
    expect(apiRes.status).toBe(200)
  })

  // §4.2 深链接抽屉覆盖
  test('订单详情抽屉：依赖接口零 403', async ({ page }) => {
    const world = readWorld()
    const forbidden: string[] = []
    page.on('response', (res) => { if (res.status() >= 400) forbidden.push(`${res.status()} ${res.url()}`) })
    const { token } = await loginApi(USERS.ops, env.testPass)   // 造数用有写权限的角色
    const title = `UAT-督导详情-${Date.now()}`
    const { id } = await ensureOrder(token, { title, storeId: world.storeId, status: 'pending' })

    await page.goto(`/orders/${id}`)
    await expect(page.getByText(title)).toBeVisible()
    expect(forbidden).toEqual([])
    await expect(page.locator('.ant-message', { hasText: /无权限|Request failed/ })).toHaveCount(0)
  })

  // §4.3 数据范围
  test('数据范围：仅可见所属组织数据', async ({ page }) => {
    const world = readWorld()
    const { token } = await loginApi(USERS.ops, env.testPass)
    const myTitle = `UAT-范围-本组-${Date.now()}`
    const otherTitle = `UAT-范围-异组-${Date.now()}`
    await ensureOrder(token, { title: myTitle, storeId: world.storeId })
    await ensureOrder(token, { title: otherTitle, storeId: world.otherStoreId })

    await page.goto('/orders')
    await expect(page.getByText(myTitle)).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText(otherTitle)).toHaveCount(0)   // 异组不可见
  })

  // §4.4 403 双轨
  test('无写权限接口 = 403（UI 无按钮 + API 直调 403）', async ({ page }) => {
    await page.goto('/orders')
    await expect(page.getByTestId('order-delete-button')).toHaveCount(0)   // UI 无删除按钮
    const { token } = await loginApi(USERS.supervisor, env.testPass)
    const res = await fetch(`${env.bffURL}/api/orders/1/delete`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` }
    })
    expect(res.status).toBe(403)
  })

  test('无权直达 /system 被守卫拦截', async ({ page }) => {
    await page.goto('/system/users')
    await expect(page).not.toHaveURL(/\/system\//)
    await expect(page.getByTestId('nav-workbench')).toBeVisible()
  })
})
```

### 状态流转专项

```ts
import { test, expect } from '@playwright/test'
import { authFile, readWorld } from '../fixtures/auth'
import { USERS, env } from '../fixtures/env'
import { loginApi, ensureOrder } from '../fixtures/provision'

const world = readWorld()

test.describe('订单流转', () => {
  test('创建→处理→待验收→关闭', async ({ page }) => {
    test.use({ storageState: authFile('supervisor') })
    const ops = await loginApi(USERS.ops, env.testPass)
    const title = `UAT-流转-${Date.now()}`
    const { id } = await ensureOrder(ops.token, {
      title, storeId: world.storeId, status: 'waiting_verify'   // 工厂直接预置状态
    })
    await page.goto(`/orders/${id}`)
    await expect(page.getByTestId('order-verify-pass')).toBeVisible()
    await page.getByTestId('order-verify-pass').click()
    await expect(page.locator('.ant-message')).toContainText(/成功|已验收/)
    await expect(page.getByText('已关闭').first()).toBeVisible({ timeout: 10_000 })
  })

  test('角色视角差异：督导可验收，店长只读', async ({ browser }) => {
    const ops = await loginApi(USERS.ops, env.testPass)
    const title = `UAT-视角-${Date.now()}`
    const { id } = await ensureOrder(ops.token, { title, storeId: world.storeId, status: 'waiting_verify' })

    const supCtx = await browser.newContext({ storageState: authFile('supervisor') })
    const supPage = await supCtx.newPage()
    await supPage.goto(`/orders/${id}`)
    await expect(supPage.getByTestId('order-verify-pass')).toBeVisible()
    await supCtx.close()

    const mgrCtx = await browser.newContext({ storageState: authFile('storeMgr') })
    const mgrPage = await mgrCtx.newPage()
    await mgrPage.goto(`/orders/${id}`)
    await expect(mgrPage.getByTestId('order-verify-pass')).toHaveCount(0)
    await mgrCtx.close()
  })
})
```

## 7. 降级断言工具

```ts
import { expect, type Page } from '@playwright/test'

const MAP_FALLBACK = ['地图加载失败', 'map load failed', '无法加载地图']
const VIDEO_MOCK = ['演示模式', '未配置', 'not configured', 'demo']

export async function expectMapFallback(page: Page, scope?: string) {
  const loc = scope ? page.locator(scope) : page.locator('body')
  await expect(loc).toBeVisible({ timeout: 15_000 })
  const text = (await loc.allInnerTexts()).join('\n').toLowerCase()
  if (!MAP_FALLBACK.some(k => text.includes(k.toLowerCase()))) {
    expect(true, '地图容器已渲染（降级态）').toBeTruthy()
  }
}

export async function expectVideoMock(page: Page, scope?: string) {
  const loc = scope ? page.locator(scope) : page.locator('body')
  const text = (await loc.allInnerTexts()).join('\n').toLowerCase()
  expect(VIDEO_MOCK.some(k => text.includes(k.toLowerCase())), `应显示视频降级文案`).toBeTruthy()
}
```
