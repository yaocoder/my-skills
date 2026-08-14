#!/usr/bin/env python3
"""
snippet-zero-noise.py — 按框架生成零噪音/深链接/数据范围断言片段，插入 spec。

用法：
  python3 snippet-zero-noise.py --framework playwright     # 默认
  python3 snippet-zero-noise.py --framework webdriverio
  python3 snippet-zero-noise.py --framework appium
  python3 snippet-zero-noise.py --framework playwright --type deep-link
  python3 snippet-zero-noise.py --framework playwright --type data-scope

输出片段写到 stdout，供复制到 spec。
"""
import argparse

PLAYWRIGHT_ZERO_NOISE = '''\
  // §4.1 首屏零噪音：落地页不得出现 >=400 响应或错误 toast
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
  const { token } = await loginApi(USERS.<role>, env.testPass)
  const apiRes = await fetch(`${env.bffURL}/api/store/options`, { headers: { Authorization: `Bearer ${token}` } })
  expect(apiRes.status).toBe(200)
'''

PLAYWRIGHT_DEEP_LINK = '''\
  // §4.2 深链接/抽屉覆盖：打开详情抽屉，依赖接口零 >=400
  const forbidden: string[] = []
  page.on('response', (res) => { if (res.status() >= 400) forbidden.push(`${res.status()} ${res.url()}`) })
  const world = readWorld()
  const { token } = await loginApi(USERS.ops, env.testPass)
  const title = `UAT-详情-${Date.now()}`
  const { id } = await ensureOrder(token, { title, storeId: world.storeId, status: 'pending' })
  await page.goto(`/orders/${id}`)
  await expect(page.getByText(title)).toBeVisible({ timeout: 15_000 })
  expect(forbidden).toEqual([])
  await expect(page.locator('.ant-message', { hasText: /无权限|Request failed/ })).toHaveCount(0)
'''

PLAYWRIGHT_DATA_SCOPE = '''\
  // §4.3 数据范围按角色隔离：本组织可见，异组织不可见
  const world = readWorld()
  const { token } = await loginApi(USERS.ops, env.testPass)
  const myTitle = `UAT-本组-${Date.now()}`
  const otherTitle = `UAT-异组-${Date.now()}`
  await ensureOrder(token, { title: myTitle, storeId: world.storeId })
  await ensureOrder(token, { title: otherTitle, storeId: world.otherStoreId })
  await page.goto('/orders')
  await expect(page.getByText(myTitle)).toBeVisible({ timeout: 15_000 })
  await expect(page.getByText(otherTitle)).toHaveCount(0)
  // API 层兜底：返回数据 storeId 全部在允许集合内
  const apiRes = await fetch(`${env.bffURL}/api/orders/list`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ page: 1, pageSize: 100 })
  })
  const data = await apiRes.json()
  const storeIds = (data.list || []).map((o: any) => o.storeId)
  expect(storeIds.every((id: number) => id === world.storeId)).toBe(true)
'''

APPIUM_ZERO_NOISE = '''\
  // §4.1 首屏零噪音（移动端无 response 监听，靠 UI 无错误 toast + API 兜底）
  await driver.activateApp('com.example.app')
  await (await driver.$('~nav-home')).waitForDisplayed({ timeout: 15000 })
  const toasts = await driver.$$('~error-toast')
  expect(toasts.length).to.equal(0)
  // API 兜底
  const { token } = await loginApi(USERS.<role>, env.testPass)
  const apiRes = await fetch(`${env.bffURL}/api/store/options`, { headers: { Authorization: `Bearer ${token}` } })
  expect(apiRes.status).to.equal(200)
'''

APPIUM_DEEP_LINK = '''\
  // §4.2 深链接：点进订单详情
  const world = readWorld()
  const { token } = await loginApi(USERS.ops, env.testPass)
  const title = `UAT-详情-${Date.now()}`
  const { id } = await ensureOrder(token, { title, storeId: world.storeId })
  await (await driver.$('~nav-orders')).click()
  await (await driver.$(`~order-row-${id}`)).click()
  await (await driver.$('~order-detail-title')).waitForDisplayed({ timeout: 15000 })
  const text = await (await driver.$('~order-detail-title')).getText()
  expect(text).to.include(title)
'''

APPIUM_DATA_SCOPE = '''\
  // §4.3 数据范围：本组织可见，异组织不可见
  const world = readWorld()
  const { token } = await loginApi(USERS.ops, env.testPass)
  const myTitle = `UAT-本组-${Date.now()}`
  const otherTitle = `UAT-异组-${Date.now()}`
  await ensureOrder(token, { title: myTitle, storeId: world.storeId })
  await ensureOrder(token, { title: otherTitle, storeId: world.otherStoreId })
  await (await driver.$('~nav-orders')).click()
  await (await driver.$(`~order-row-title-${myTitle}`)).waitForDisplayed({ timeout: 15000 })
  const otherRows = await driver.$$(`~order-row-title-${otherTitle}`)
  expect(otherRows.length).to.equal(0)
'''

SNIPPETS = {
    'playwright': {'zero-noise': PLAYWRIGHT_ZERO_NOISE, 'deep-link': PLAYWRIGHT_DEEP_LINK, 'data-scope': PLAYWRIGHT_DATA_SCOPE},
    'webdriverio': {'zero-noise': PLAYWRIGHT_ZERO_NOISE.replace('page.', 'browser.').replace("page.on('response'", "browser.on('response'"), 'deep-link': PLAYWRIGHT_DEEP_LINK, 'data-scope': PLAYWRIGHT_DATA_SCOPE},
    'appium': {'zero-noise': APPIUM_ZERO_NOISE, 'deep-link': APPIUM_DEEP_LINK, 'data-scope': APPIUM_DATA_SCOPE},
}

def main():
    ap = argparse.ArgumentParser(description="生成零噪音/深链接/数据范围断言片段")
    ap.add_argument("--framework", default="playwright", choices=["playwright", "webdriverio", "appium"])
    ap.add_argument("--type", default="zero-noise", choices=["zero-noise", "deep-link", "data-scope"])
    args = ap.parse_args()
    print(SNIPPETS[args.framework][args.type])

if __name__ == "__main__":
    main()
