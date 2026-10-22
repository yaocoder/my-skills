# -*- coding: utf-8 -*-
"""render_check — 把 .pptx 逐页渲染成 PNG 供目检（多后端自动降级）。

用法:
    python3 render_check.py deck.pptx --out ./pages [--scale 1.4]

后端优先级:
    1. LibreOffice (soffice / libreoffice)  — 跨平台首选
    2. macOS PowerPoint (AppleScript 导 PDF) — 需本机装有 PowerPoint
    3. qlmanage 封面缩略图                  — 兜底（仅第 1 页）
PDF -> PNG 统一使用 pypdfium2（pip install pypdfium2），无需系统 poppler。
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time


def log(msg):
    print(f"[render_check] {msg}")


# ---------- 后端 1: LibreOffice ----------
def export_pdf_soffice(pptx, pdf):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    workdir = os.path.dirname(os.path.abspath(pptx))
    with tempfile.TemporaryDirectory() as td:
        cmd = [exe, "--headless", "--convert-to", "pdf", "--outdir", td,
               os.path.abspath(pptx)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                           cwd=workdir)
        produced = [f for f in os.listdir(td) if f.lower().endswith(".pdf")]
        if r.returncode == 0 and produced:
            shutil.move(os.path.join(td, produced[0]), pdf)
            return pdf
    return None


# ---------- 后端 2: macOS PowerPoint ----------
APPLESCRIPT = '''
on run argv
    set pptxPath to item 1 of argv
    set pdfPath to item 2 of argv
    with timeout of 240 seconds
        tell application "Microsoft PowerPoint"
            open (POSIX file pptxPath)
            delay 4
            save active presentation in (POSIX file pdfPath) as save as PDF
            delay 2
            close active presentation saving no
        end tell
    end timeout
end run
'''


def export_pdf_powerpoint(pptx, pdf):
    if sys.platform != "darwin":
        return None
    if not os.path.exists("/Applications/Microsoft PowerPoint.app"):
        return None
    # 防御：先退出可能残留的 PowerPoint，避免导出「已打开的旧副本」而非磁盘新文件
    try:
        subprocess.run(["osascript", "-e",
                        'tell application "Microsoft PowerPoint" to quit saving no'],
                       capture_output=True, text=True, timeout=30)
        time.sleep(2)
    except Exception:
        pass
    subprocess.run(["pkill", "-9", "-f", "Microsoft PowerPoint"],
                   capture_output=True, text=True)
    time.sleep(1)
    for attempt in (1, 2):
        try:
            r = subprocess.run(
                ["osascript", "-e", APPLESCRIPT,
                 os.path.abspath(pptx), os.path.abspath(pdf)],
                capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and os.path.exists(pdf):
                return pdf
            log(f"PowerPoint 导出失败(第{attempt}次): {r.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            log(f"PowerPoint 导出超时(第{attempt}次)")
        time.sleep(2)
    # 逃生：文档可能仍处于打开状态，尝试直接从当前文稿导出
    try:
        r = subprocess.run([
            "osascript", "-e",
            'tell application "Microsoft PowerPoint" to quit saving no'],
            capture_output=True, text=True, timeout=30)
        time.sleep(2)
    except Exception:
        pass
    return None


# ---------- 后端 3: qlmanage 封面 ----------
def thumbnail_qlmanage(pptx, outdir):
    out = os.path.join(outdir, "qlmanage")
    os.makedirs(out, exist_ok=True)
    r = subprocess.run(["qlmanage", "-t", "-s", "1800", "-o", out,
                        os.path.abspath(pptx)],
                       capture_output=True, text=True, timeout=120)
    pngs = [f for f in os.listdir(out) if f.lower().endswith(".png")]
    if pngs:
        shutil.move(os.path.join(out, pngs[0]), os.path.join(outdir, "p01.png"))
        return True
    return False


# ---------- PDF -> PNG ----------
def render_pdf(pdf, outdir, scale):
    try:
        import pypdfium2 as pdfium
    except ImportError:
        sys.exit("缺少依赖: pip install pypdfium2")
    os.makedirs(outdir, exist_ok=True)
    doc = pdfium.PdfDocument(pdf)
    for i in range(len(doc)):
        dest = os.path.join(outdir, f"p{i+1:02d}.png")
        doc[i].render(scale=scale).to_pil().save(dest)
    return len(doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--out", default="./pages")
    ap.add_argument("--scale", type=float, default=1.4)
    args = ap.parse_args()

    pptx = os.path.abspath(args.pptx)
    outdir = os.path.abspath(args.out)
    os.makedirs(outdir, exist_ok=True)
    pdf = os.path.join(outdir, "deck.pdf")

    for backend, fn in (("LibreOffice", export_pdf_soffice),
                        ("PowerPoint", export_pdf_powerpoint)):
        log(f"尝试后端: {backend} ...")
        if fn(pptx, pdf):
            n = render_pdf(pdf, outdir, args.scale)
            log(f"完成: {backend} -> {outdir}/p01..p{n:02d}.png")
            return

    log("PDF 导出均失败，降级为 qlmanage 封面缩略图（仅第 1 页）")
    if thumbnail_qlmanage(pptx, outdir):
        log(f"完成(仅封面): {outdir}/p01.png")
        return
    sys.exit("所有渲染后端均失败。请安装 LibreOffice，或检查 PowerPoint 是否有弹窗阻塞。")


if __name__ == "__main__":
    main()
