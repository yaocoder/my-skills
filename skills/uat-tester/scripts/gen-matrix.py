#!/usr/bin/env python3
"""
gen-matrix.py — 交互式生成 UAT 用例追溯矩阵 Markdown 骨架。

用法：
  python3 gen-matrix.py [--roles roles.json] [--modules "AUTH,MENU,DASH,STORE,SEC,OPS,BIZ,DEV,SYS,V,MOBILE"]
  python3 gen-matrix.py --demo     # 用内置演示数据生成一份可参考的矩阵

输出写到 stdout，建议重定向到 docs/uat/matrix.md。
"""
import argparse, json, sys
from datetime import date

DEMO_ROLES = [
    {"code": "ROLE_ADMIN", "name": "超级管理员", "menus": "全部", "scope": "ALL", "write": "全部", "invisible": "—", "forbidden_403": "—"},
    {"code": "ROLE_OPS", "name": "业务运营", "menus": "运营/门店/告警", "scope": "ALL", "write": "订单CRUD/告警处理", "invisible": "系统/设备", "forbidden_403": "系统设置"},
    {"code": "ROLE_REGION", "name": "区域经理", "menus": "运营/门店/告警", "scope": "ORG(本区及下级)", "write": "订单", "invisible": "系统/设备", "forbidden_403": "跨区订单"},
    {"code": "ROLE_SUPERVISOR", "name": "督导", "menus": "运营/告警", "scope": "ORG(本组织)", "write": "订单验收/名单申报", "invisible": "门店管理/系统/设备", "forbidden_403": "订单删除/系统"},
    {"code": "ROLE_STORE_MGR", "name": "店长", "menus": "告警/运营/经营", "scope": "STORE(本店)", "write": "名单申报", "invisible": "门店管理/系统/设备", "forbidden_403": "订单验收/删除"},
    {"code": "ROLE_SECURITY", "name": "安全员", "menus": "安全中心", "scope": "ALL", "write": "告警处理/名单审批", "invisible": "门店/系统/设备", "forbidden_403": "订单"},
    {"code": "ROLE_IT", "name": "IT管理员", "menus": "系统/设备", "scope": "ALL", "write": "用户/角色/设备", "invisible": "业务模块", "forbidden_403": "订单/告警"},
    {"code": "DISABLED", "name": "禁用账号", "menus": "—", "scope": "—", "write": "—", "invisible": "全部", "forbidden_403": "—（登录即拒）"},
]

DEMO_MODULES = ["AUTH", "MENU", "DASH", "STORE", "SEC", "OPS", "BIZ", "DEV", "SYS", "V", "MOBILE"]

DEMO_ACCEPTS = [
    ("AUTH-01", "P0", "登录页可访问、表单齐全"),
    ("AUTH-02", "P0", "正确账号密码登录成功"),
    ("AUTH-03", "P0", "错误密码登录失败"),
    ("AUTH-04", "P0", "禁用账号登录被拒"),
    ("AUTH-05", "P0", "未登录访问受保护页跳登录"),
    ("AUTH-06", "P0", "登录后按权限落地页"),
    ("AUTH-07", "P0", "登出返回登录页"),
    ("MENU-01", "P0", "各角色菜单可见性按矩阵"),
    ("MENU-02", "P0", "无权直达URL被守卫拦截"),
]

def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    return "\n".join(out)

def gen(roles, modules, demo=False):
    lines = []
    lines.append(f"# UAT 用例追溯矩阵\n\n> 生成日期：{date.today()}\n> 工具：uat-tester/scripts/gen-matrix.py\n\n---\n")
    lines.append("## 1. 角色矩阵\n\n")
    lines.append(md_table(["角色", "编号", "可见菜单", "数据范围", "关键写权限", "不可见/无权直达", "写=403的接口"],
                          [{"角色": r["name"], "编号": r["code"], "可见菜单": r.get("menus",""), "数据范围": r.get("scope",""), "关键写权限": r.get("write",""), "不可见/无权直达": r.get("invisible",""), "写=403的接口": r.get("forbidden_403","")} for r in roles]))
    lines.append("\n\n> 数据范围枚举：ALL=全量 / ORG=本组织及下级 / STORE=本店 / SELF=本人\n\n---\n")
    lines.append("## 2. 验收清单\n\n")
    accepts = DEMO_ACCEPTS if demo else [(f"{m}-01", "P0", f"{m} 用例待填充") for m in modules]
    lines.append(md_table(["验收项", "优先级", "说明"], [{"验收项": a[0], "优先级": a[1], "说明": a[2]} for a in accepts]))
    lines.append("\n\n---\n\n## 3. 用例追溯矩阵\n\n> 用例编号 `UAT-<组>-<n>`；状态：✅ 已覆盖 / 🅿️ P0本批 / ⏳ 二期 / ❌ 不测\n\n")
    lines.append(md_table(["验收项", "优先级", "用例", "状态", "实现文件"],
                          [{"验收项": a[0], "优先级": a[1], "用例": f"UAT-{a[0].split('-')[0]}-{a[0].split('-')[1]}", "状态": "🅿️", "实现文件": "待创建"} for a in accepts]))
    lines.append("\n\n---\n\n## 4. 四原则落地清单\n\n")
    lines.append(md_table(["角色/模块", "零噪音用例", "深链接入口", "数据范围断言", "幂等造数"],
                          [{"角色/模块": r["name"], "零噪音用例": "待补", "深链接入口": "待补", "数据范围断言": "待补", "幂等造数": "待补"} for r in roles if r["code"] != "DISABLED"]))
    lines.append("\n\n---\n\n## 5. 不测范围\n\n- 移动端原生（本期不测的端）\n- WebSocket 实时推送的 UI 呈现\n- 真实地图/视频流播放（断降级占位）\n- 真实第三方支付/短信\n- 改密/删账号等破坏性操作\n")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description="生成 UAT 用例追溯矩阵骨架")
    ap.add_argument("--roles", help="角色 JSON 文件路径（数组，字段见 demo）")
    ap.add_argument("--modules", help="模块域前缀，逗号分隔", default="AUTH,MENU,DASH,STORE,SEC,OPS,BIZ,DEV,SYS,V,MOBILE")
    ap.add_argument("--demo", action="store_true", help="用内置演示数据生成")
    args = ap.parse_args()
    roles = DEMO_ROLES if args.demo or not args.roles else json.load(open(args.roles))
    modules = [m.strip() for m in args.modules.split(",")]
    print(gen(roles, modules, demo=args.demo))

if __name__ == "__main__":
    main()
