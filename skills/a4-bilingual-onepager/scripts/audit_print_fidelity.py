#!/usr/bin/env python3
"""打印保真审计：拦住「浏览器里好好的、导出 PDF 就变形」的写法。

检查三类已知会让 PDF 与网页不一致的问题（均在真实项目里踩过）：

1. box-shadow 未在 @media print 关闭
   → PDF 里彩色/大模糊阴影会被打印成**实心方块**，小元素（编号徽章）看着像错位。
2. 小尺寸元素用 border-radius:50% 画圆点
   → 3–8px 的圆角在 PDF 里被拉成胶囊/竖条，改用 SVG data-uri 背景。
3. 缺 print-color-adjust:exact
   → Chrome 默认不打印背景，渐变/色块整片消失。

用法：
    python3 scripts/audit_print_fidelity.py onepager.html

退出码：0 = 通过；1 = 有硬问题（禁止导出 PDF）。
"""

import re
import sys


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def css_text(html: str) -> str:
    """把 <style> 内容拼起来；没有 style 标签时按整份文件当 CSS。"""
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)
    return strip_comments("\n".join(blocks) if blocks else html)


def find_block(css: str, start: int) -> str:
    """从 start（指向 '{'）取出配平的块内容。"""
    depth, i = 0, start
    while i < len(css):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[start + 1 : i]
        i += 1
    return css[start + 1 :]


def media_print_blocks(css: str):
    """产出所有 @media print 块的内容。"""
    for m in re.finditer(r"@media[^{]*print[^{]*\{", css, flags=re.I):
        yield find_block(css, m.end() - 1)


def rules(css: str):
    """产出 (selector, body)，跳过 @ 规则自身的头部。"""
    clean = re.sub(r"@media[^{]*\{", "{", css)  # 展开 media 包裹，便于逐条扫
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", clean):
        sel, body = m.group(1).strip(), m.group(2)
        if sel.startswith("@"):
            continue
        yield sel, body


def px(value: str):
    m = re.search(r"(-?[\d.]+)\s*px", value)
    return float(m.group(1)) if m else None


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 scripts/audit_print_fidelity.py <onepager.html>")
        return 2

    path = sys.argv[1]
    html = open(path, encoding="utf-8").read()
    css = css_text(html)
    print_blocks = list(media_print_blocks(css))
    print_css = "\n".join(print_blocks)

    problems, warnings = [], []

    # 1) box-shadow 必须在 @media print 里关掉
    has_shadow = re.search(r"box-shadow\s*:\s*(?!none)", css) is not None
    shadow_off = re.search(r"box-shadow\s*:\s*none", print_css) is not None
    if has_shadow and not shadow_off:
        problems.append(
            "box-shadow 未在 @media print 中关闭 —— PDF 里会被打印成实心方块"
            "（小徽章尤其明显，视觉上像错位）。修法：\n"
            "    @media print { * { box-shadow: none !important; } }"
        )

    # 2) 小尺寸圆点不要用 border-radius:50%
    tiny_dots = []
    for sel, body in rules(css):
        if not re.search(r"border-radius\s*:\s*50%", body):
            continue
        w = px(re.search(r"(?<![-\w])width\s*:\s*([^;]+)", body).group(1)) if re.search(r"(?<![-\w])width\s*:\s*([^;]+)", body) else None
        h = px(re.search(r"(?<![-\w])height\s*:\s*([^;]+)", body).group(1)) if re.search(r"(?<![-\w])height\s*:\s*([^;]+)", body) else None
        if w is not None and h is not None and w <= 8 and h <= 8:
            tiny_dots.append((sel, w, h))
    if tiny_dots:
        detail = "、".join(f"{s}（{w:g}×{h:g}px）" for s, w, h in tiny_dots[:6])
        problems.append(
            f"小尺寸圆点用 border-radius:50% 绘制：{detail}\n"
            "    PDF 里会被拉成胶囊/竖条。修法：改用 SVG 矢量背景，例如\n"
            "    background:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
            "viewBox='0 0 4 4'%3E%3Ccircle cx='2' cy='2' r='2' fill='%232563EB'/%3E%3C/svg%3E\") "
            "no-repeat center/4px 4px;"
        )

    # 3) print-color-adjust（背景能在 PDF 里保留的前提）
    if not re.search(r"print-color-adjust\s*:\s*exact", print_css):
        problems.append(
            "缺少 print-color-adjust:exact —— 打印时背景/渐变会整片消失。\n"
            "    修法：@media print { * { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }"
        )

    # 提示项（不阻断）：负偏移装饰可能触发 scrollHeight 假警报
    if re.search(r"(right|bottom)\s*:\s*-\d", css):
        warnings.append(
            "存在 right/bottom 负偏移的装饰元素 —— 若在 overflow:hidden 容器内，"
            "measure_layout 可能报假 CLIPPED；装饰越界尽量朝左上（top/left 负值）。"
        )

    for w in warnings:
        print(f"⚠️  {w}")
    for p in problems:
        print(f"❌ {p}")

    if problems:
        print(f"\n❌ 打印保真审计未通过：{len(problems)} 个问题（导出 PDF 前必须修）")
        return 1

    print("✅ 打印保真审计通过：阴影已关闭、无小圆角圆点、背景打印已开启。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
