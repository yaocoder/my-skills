# 移动 App（iOS/Android）UAT 模板

> 移动端 UAT 与 Web 的差异：选择器用 `testID/accessibilityIdentifier`、storageState 复用受限、多设备 project、网络监听需框架支持。

---

## 1. 框架选型表

| 被测栈 | 推荐框架 | 选择器约定 | storageState |
|---|---|---|---|
| React Native | Detox | `testID` | launchArgs（有限） |
| iOS 原生 | XCUITest 或 Appium | `accessibilityIdentifier` | 不支持，重启 app 复用登录态 |
| Android 原生 | Espresso/UIAutomator 或 Appium | `testId`/`tag` | 不支持 |
| 跨端统一（推荐） | Appium（WebDriverIO 驱动） | 统一 `testId` | 不支持，靠 app 重启 + 持久 token |
| Flutter | integration_test | `Key`/`ValueKey` | 不支持 |

> 默认推荐 **Appium + WebDriverIO**：跨 iOS/Android 统一、可与 Web 用例同框架管理、CI 友好。RN 项目优先 **Detox**（更快的原生交互）。

## 2. 选择器约定（跨平台统一）

为了 Web/App 用例可复用断言逻辑，统一约定：

- iOS：`accessibilityIdentifier = "login-submit"`
- Android：`tag = "login-submit"` 或 `testId`
- RN：`testID = "login-submit"`
- Flutter：`Key("login-submit")`

Appium 的 accessibility locator 可同时命中 iOS 的 `accessibilityIdentifier` 与 Android 的 `tag`，实现跨平台统一。

## 3. 目录结构

```
e2e/
├── global-setup.ts          # 幂等预置（走后端 API，与 Web 共用）
├── fixtures/
│   ├── env.ts
│   ├── api.ts               # 与 Web 共用
│   ├── auth.ts              # 不写 storageState，改写「持久 token 文件」供 app 注入
│   └── provision.ts         # 与 Web 共用
├── pages/                   # POM（用 Appium locator）
└── specs/
    ├── auth.spec.ts
    ├── rbac-<role>.spec.ts
    └── journeys/
```

## 4. Appium 配置骨架

```ts
// wdio.conf.ts
export const config = {
  runner: 'local',
  specs: ['./e2e/specs/**/*.spec.ts'],
  maxInstances: 1,                    // 串行，避免写冲突
  capabilities: [
    { platformName: 'iOS', 'appium:platformVersion': '17.0',
      'appium:deviceName': 'iPhone 15',
      'appium:app': './app/Test.app', 'appium:automationName': 'XCUITest' },
    { platformName: 'Android', 'appium:platformVersion': '14',
      'appium:deviceName': 'Pixel 8', 'appium:app': './app/Test.apk',
      'appium:automationName': 'UiAutomator2' }
  ],
  services: ['appium'],
  framework: 'mocha',
  timeout: 90000,
  mochaOpts: { timeout: 90000 },
  reporters: [['spec'], ['allure', { outputDir: 'allure-results' }]],
  // 失败截图/视频
  afterTest: async function (test, _ctx, { error }) {
    if (error) {
      await browser.saveScreenshot(`./test-results/${test.title}.png`)
    }
  }
}
```

## 5. auth 策略（移动端无 storageState）

移动端不能像 Web 那样写 localStorage storageState。两种方案：

### 方案 A：app 启动注入 token（推荐，最快）

后端 globalSetup 预置角色 → 把 token 写文件 → app 启动时读 launchArgs/env 注入，跳过登录页直接进首页。

```ts
// fixtures/auth.ts
import fs from 'node:fs'
import { env, USERS, type RoleKey } from './env'
import { loginApi } from './api'

const TOKEN_DIR = './.auth'
export function tokenFile(role: RoleKey) { return `${TOKEN_DIR}/${role}.token` }

export async function writeTokens() {
  fs.mkdirSync(TOKEN_DIR, { recursive: true })
  for (const [role, username] of Object.entries(USERS) as [RoleKey, string][]) {
    if (role === 'disabled') continue
    const { token } = await loginApi(username, env.testPass)
    fs.writeFileSync(tokenFile(role), token)
  }
}

// wdio capability 里注入：
// 'appium:launchArgs': { '-testToken': fs.readFileSync(tokenFile('reviewer'), 'utf8') }
```

### 方案 B：UI 登录（每用例重复，最稳但慢）

```ts
export async function loginViaUi(driver: WebdriverIO.Browser, username: string, password: string) {
  await driver.$('~login-username').setValue(username)
  await driver.$('~login-password').setValue(password)
  await driver.$('~login-submit').click()
  await driver.$('~nav-dashboard').waitForDisplayed({ timeout: 15000 })
}
```

## 6. POM 模板（Appium locator）

```ts
import type { WebdriverIOBrowser } from 'webdriverio'

export class AppLayout {
  constructor(private readonly d: WebdriverIOBrowser) {}

  async gotoMenu(key: string) {
    const item = await this.d.$(`~nav-${key}`)   // ~ 命中 accessibility id
    await item.click()
    await item.waitForDisplayed()
  }

  async logout() {
    await (await this.d.$('~user-btn')).click()
    await (await this.d.$('~logout')).click()
    await (await this.d.$('~login-submit')).waitForDisplayed()
  }
}
```

## 7. spec 骨架（零噪音/深链接/数据范围同样适用）

```ts
import { expect } from 'chai'
import { tokenFile } from '../fixtures/auth'
import { readWorld } from '../fixtures/auth'
import { ensureResource } from '../fixtures/provision'
import { loginApi } from '../fixtures/api'
import { USERS, env } from '../fixtures/env'

describe('审核者角色权限专项', () => {
  // §4.1 首屏零噪音：app 启动后首页不得弹错误 toast
  it('落地页零噪音', async () => {
    // 注入 reviewer token 启动 app（capability 配 -testToken）
    await driver.activateApp('com.example.app')
    await (await driver.$('~nav-dashboard')).waitForDisplayed({ timeout: 15000 })
    // 断言无错误 toast（按实际 UI 元素）
    const toasts = await driver.$$('~error-toast')
    expect(toasts.length).to.equal(0)
  })

  // §4.2 深链接：点进资源详情
  it('资源详情：依赖数据加载无错误', async () => {
    const world = readWorld()
    const { token } = await loginApi(USERS.admin, env.testPass)
    const title = `UAT-详情-${Date.now()}`
    const { id } = await ensureResource(token, { title, deptId: world.deptId })
    await (await driver.$('~nav-resources')).click()
    await (await driver.$(`~resource-row-${id}`)).click()
    await (await driver.$('~resource-detail-title')).waitForDisplayed({ timeout: 15000 })
    const text = await (await driver.$('~resource-detail-title')).getText()
    expect(text).to.include(title)
  })

  // §4.3 数据范围
  it('数据范围：仅可见本组织资源', async () => {
    const world = readWorld()
    const { token } = await loginApi(USERS.admin, env.testPass)
    const myTitle = `UAT-本组-${Date.now()}`
    const otherTitle = `UAT-异组-${Date.now()}`
    await ensureResource(token, { title: myTitle, deptId: world.deptId })
    await ensureResource(token, { title: otherTitle, deptId: world.otherDeptId })
    await (await driver.$('~nav-resources')).click()
    const myRow = await driver.$(`~resource-row-title-${myTitle}`)
    await myRow.waitForDisplayed({ timeout: 15000 })
    const otherRow = await driver.$$(`~resource-row-title-${otherTitle}`)
    expect(otherRow.length).to.equal(0)
  })
})
```

## 8. 移动端特有注意

- **网络监听**：Appium 无法像 Playwright 那样直接 `page.on('response')`。零噪音断言改为：UI 层断言无错误 toast + 启动后调后端接口层断言角色 token 可用。
- **多设备 project**：iOS/Android 分 capabilities，CI 矩阵跑两份。
- **真机/模拟器**：CI 默认模拟器（快、可重复）；真机冒烟标 `@live` 默认排除。
- **推送**：移动端推送的 UI 呈现本期不测，状态流转以 API/页面结果为准（与 Web 一致）。
- **生物认证/权限弹窗**：app 首次启动的系统权限弹窗（相机/通知/位置）用 `autoAcceptAlerts: true` 自动通过；生物认证用 mock 或跳过。