#!/usr/bin/env python3
"""A4 一页纸版面测量：natural 趟（自然高度总账）+ rendered 趟（裁切/溢出）。

用法:
  python3 measure_layout.py page.html [--page-height 1123] [--chrome /path/to/chrome]

两趟测量回答两个问题：
  natural  —— 所有区块按自然高度排，总和超没超 1123？（超了渲染时必被压缩/裁切）
  rendered —— 按真实 CSS 渲染，页脚有没有被顶出页外？overflow:hidden 里有没有文字被裁？

退出码: 0 = 全部通过；1 = 存在超预算 / 裁切 / 溢出（禁止导出 PDF）。
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE_JS = r"""
<script>
window.addEventListener('load', function () {
  var mode = '__MODE__', target = __TARGET__, lines = [];
  document.querySelectorAll('.page').forEach(function (p) {
    if (mode === 'natural') {
      var sum = 0, parts = [];
      Array.prototype.forEach.call(p.children, function (c) {
        var s = getComputedStyle(c), h = c.offsetHeight;
        var mt = parseFloat(s.marginTop) || 0, mb = parseFloat(s.marginBottom) || 0;
        sum += h + mt + mb;
        var name = (c.className || c.tagName).split(' ')[0];
        parts.push('    ' + name + ':' + Math.round(h) +
          (mt ? ' +mt' + Math.round(mt) : '') + (mb ? ' +mb' + Math.round(mb) : ''));
      });
      var over = Math.round(sum) - target;
      lines.push('[natural] ' + (p.id || p.className) + ' TOTAL=' + Math.round(sum) +
        (over > 0 ? '  OVER+' + over : '  ok 余量' + (-over) + 'px'));
      parts.forEach(function (x) { lines.push(x); });
    } else {
      var pr = p.getBoundingClientRect();
      var foot = p.querySelector('.footer') || p.lastElementChild;
      var fr = foot.getBoundingClientRect();
      var diff = Math.round(fr.bottom - pr.bottom);
      lines.push('[rendered] ' + (p.id || p.className) + '  页脚底-页底=' + diff +
        (Math.abs(diff) <= 1 ? '  ok' : (diff > 0 ? '  页脚被顶出页外!' : '  页脚未贴底(底部留白)')));
      var els = [p].concat(Array.prototype.slice.call(p.querySelectorAll('*')));
      els.forEach(function (el) {
        var s = getComputedStyle(el);
        if (s.overflow !== 'hidden' && s.overflowY !== 'hidden') return;
        if (el.clientHeight <= 0) return;
        if (el.scrollHeight > el.clientHeight + 2)
          lines.push('    CLIPPED ' + (el.className || el.tagName) +
            ' scroll=' + el.scrollHeight + ' client=' + el.clientHeight);
      });
      Array.prototype.forEach.call(p.children, function (c) {
        var r = c.getBoundingClientRect();
        if (r.bottom > pr.bottom + 1)
          lines.push('    BLEED ' + (c.className || c.tagName) +
            ' 越出页底 ' + Math.round(r.bottom - pr.bottom) + 'px');
      });
    }
  });
  var pre = document.createElement('pre');
  pre.id = 'probe-out';
  pre.textContent = lines.join('\n');
  document.body.appendChild(pre);
});
</script>
"""

NATURAL_CSS = """
<style id="probe-override">
.page > * { flex: none !important; }
.page { height: auto !important; }
</style>
"""


def find_chrome(explicit):
    for cand in (explicit, os.environ.get("CHROME"), MAC_CHROME):
        if cand and os.path.exists(cand):
            return cand
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("找不到 Chrome：用 --chrome 参数或 CHROME 环境变量指定可执行文件路径")


def run_probe(chrome, src_path, mode, target):
    """注入探针 → headless dump-dom → 解析 #probe-out 文本。"""
    src = open(src_path, encoding="utf-8").read()
    probe = PROBE_JS.replace("__MODE__", mode).replace("__TARGET__", str(target))
    override = NATURAL_CSS if mode == "natural" else ""
    # 临时文件必须与源文件同目录，保证 ../assets/ 相对路径可用
    base = os.path.basename(src_path)
    tmp = os.path.join(os.path.dirname(src_path) or ".", f".probe-{mode}-{base}")
    open(tmp, "w", encoding="utf-8").write(
        src.replace("</body>", override + probe + "</body>"))
    try:
        out = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--dump-dom",
             "--virtual-time-budget=3000", f"file://{os.path.abspath(tmp)}"],
            capture_output=True, text=True, timeout=60)
        m = re.search(r'<pre id="probe-out">(.*?)</pre>', out.stdout, re.S)
        if not m:
            sys.exit(f"探针未输出（{mode} 趟）。stderr: {out.stderr[:500]}")
        return html.unescape(m.group(1))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--page-height", type=int, default=1123)
    ap.add_argument("--chrome", default=None)
    args = ap.parse_args()

    chrome = find_chrome(args.chrome)
    print(f"== natural 趟（自然高度总账，目标 {args.page_height}px）==")
    natural = run_probe(chrome, args.html, "natural", args.page_height)
    print(natural)
    print("== rendered 趟（真实渲染：裁切/溢出）==")
    rendered = run_probe(chrome, args.html, "rendered", args.page_height)
    print(rendered)

    fails = []
    for line in natural.splitlines():
        if "OVER+" in line:
            fails.append(line.strip())
    for line in rendered.splitlines():
        if "CLIPPED" in line or "BLEED" in line or "被顶出" in line:
            fails.append(line.strip())
    if fails:
        print("\n❌ 未通过：")
        for f in fails:
            print("  -", f)
        print("  修法：收区块内边距/字号、减内容，或调整唯一弹性区；改完重跑本脚本。")
        sys.exit(1)
    print("\n✅ 版面通过：无超预算、无裁切、页脚贴底。")


if __name__ == "__main__":
    main()
