#!/usr/bin/env python3
"""打印对比度审计：抽取 HTML/CSS 里的文字色，输出对各背景色的对比度矩阵。

用法:
  python3 audit_contrast.py onepager.html [--min 4.5]

背景候选 = 样式里出现的所有实色背景 + 白底。判定按亮度分组（减少误报）：
  深字（lum≤0.35）只查浅底、浅字（lum≥0.55）只查深底、中间色查全部——
  深色正文不会用在 chip 蓝底上，拿全矩阵配对只会产生噪音。
  - 对其「应出现的底色组」里任何背景都达不到阈值 → 硬失败（放哪都发虚）；
  - 只对组内部分背景达标 → 通过但打印矩阵与使用它的选择器，人工核对实际底色。

退出码: 0 = 无硬失败；1 = 存在任何底色都不可达阈值的文字色。
"""
import argparse
import re
import sys

HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;}]+)")
VAR_USE_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*((?:[^()]|\([^()]*\))*))?\)")
COLOR_PROP_RE = re.compile(r"(?<![-\w])color\s*:\s*([^;]+)")
BG_PROP_RE = re.compile(r"background(?:-color)?\s*:\s*([^;]+)")
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
NAMED = {"white": "#FFFFFF", "black": "#000000"}
LIGHT_BG_LUM = 0.55  # 背景亮暗分界：≥ 视为浅底


def norm_hex(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def resolve(value, vars_map, depth=0):
    """把 var(--x, fallback) 与 rgb() 解析成十六进制，解析不了返回 None。"""
    v = value.strip()
    while "var(" in v and depth < 10:
        m = VAR_USE_RE.search(v)
        if not m:
            return None
        name, fallback = m.group(1), m.group(2)
        repl = vars_map.get(name, fallback if fallback else "")
        v = (v[:m.start()] + repl.strip() + v[m.end():]).strip()
        depth += 1
    v = v.strip().lower()
    if v in NAMED:
        return NAMED[v]
    if v.startswith("rgb"):
        nums = re.findall(r"[\d.]+", v)
        if len(nums) >= 3:
            r, g, b = (int(float(x)) for x in nums[:3])
            return f"#{r:02X}{g:02X}{b:02X}"
        return None
    m = HEX_RE.search(v)
    if m and "gradient" not in v and "url" not in v:
        return norm_hex(m.group(1))
    if "gradient" in v:  # 渐变取第一个色标作近似背景
        m = HEX_RE.search(v)
        return norm_hex(m.group(1)) if m else None
    return None


def luminance(hex_color):
    h = hex_color.lstrip("#")
    chan = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in chan)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--min", type=float, default=4.5)
    args = ap.parse_args()

    src = open(args.html, encoding="utf-8").read()
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))
    inline_styles = re.findall(r'style="([^"]+)"', src)
    all_decls = css + "\n" + "\n".join(inline_styles)

    vars_map = {}
    for name, val in VAR_DEF_RE.findall(all_decls):
        if "#" in val or "rgb" in val:
            vars_map.setdefault(name, val)

    backgrounds = {"#FFFFFF"}  # 白底恒为候选
    text_colors = {}  # hex -> [selectors]
    for m in RULE_RE.finditer(css):
        selector, body = m.group(1).strip().replace("\n", " "), m.group(2)
        for bm in BG_PROP_RE.finditer(body):
            hx = resolve(bm.group(1), vars_map)
            if hx:
                backgrounds.add(hx)
        cm = COLOR_PROP_RE.search(body)
        if cm:
            hx = resolve(cm.group(1), vars_map)
            if hx:
                text_colors.setdefault(hx, []).append(selector[:70])
    for decl in inline_styles:  # 内联 style 里的直接文字色（少见但兜底）
        cm = COLOR_PROP_RE.search(decl)
        if cm:
            hx = resolve(cm.group(1), vars_map)
            if hx:
                text_colors.setdefault(hx, []).append("(inline style)")

    bg_list = sorted(backgrounds, key=luminance, reverse=True)

    def plausible_group(text_hex):
        """按文字亮度挑它「应出现的底色组」：深字查浅底、浅字查深底、中间色查全部。"""
        lum = luminance(text_hex)
        if lum <= 0.35:
            group = [b for b in bg_list if luminance(b) >= LIGHT_BG_LUM]
            label = "浅底组"
        elif lum >= LIGHT_BG_LUM:
            group = [b for b in bg_list if luminance(b) < LIGHT_BG_LUM]
            label = "深底组"
        else:
            group, label = bg_list, "全部(中间色)"
        return group or bg_list, label

    print(f"背景候选 {len(bg_list)} 个: {', '.join(bg_list)}")
    print(f"文字色 {len(text_colors)} 个，阈值 {args.min}:1"
          "（深字查浅底 / 浅字查深底 / 中间色查全部）\n")
    hard_fail, partial = [], []
    for color in sorted(text_colors, key=luminance):
        group, label = plausible_group(color)
        ratios = {b: contrast(color, b) for b in group}
        cells = "  ".join(
            f"{b}={r:.2f}{'✅' if r >= args.min else '❌'}" for b, r in ratios.items())
        if max(ratios.values()) < args.min:
            hard_fail.append(color)
            print(f"❌ {color} [{label}] 任何底色都不达标: {cells}")
        elif min(ratios.values()) < args.min:
            partial.append(color)
            print(f"⚠️  {color} [{label}] 仅组内部分底色达标: {cells}")
        else:
            print(f"✅ {color} [{label}] 全部达标: {cells}")
        for sel in dict.fromkeys(text_colors[color]):
            print(f"      用在: {sel}")

    if hard_fail:
        print(f"\n❌ {len(hard_fail)} 个文字色对所有底色都 < {args.min}:1"
              "（PDF 必发虚）——加深颜色或改用已达标令牌，改完重跑。")
        sys.exit(1)
    if partial:
        print(f"\n⚠️  {len(partial)} 个颜色只对部分底色达标——逐一核对上面"
              "「用在」的选择器确实位于其达标底色上（深底专用色出现在白底 = 发虚）。")
    print("\n✅ 无硬失败。")


if __name__ == "__main__":
    main()
