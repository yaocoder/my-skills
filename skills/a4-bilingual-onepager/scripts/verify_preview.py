#!/usr/bin/env python3
"""一页纸预览图验收：尺寸 / 页边距无内容渗出 / 页面区域非空白。

用法:
  python3 verify_preview.py preview-zh.png [--width 794] [--page-height 1123] [--margin 24]

预览图结构 = 上边距 + A4 页面 + 下边距（build.sh 用 window-size 截图产生）。
任何一项不过即退出码 1。

检查项：
  1. 图像尺寸 == width × (page-height + 2×margin)
  2. 上下边距带颜色均匀 —— 不均匀说明有内容渗出页外（版面溢出的直接证据）
  3. 页面区域非纯色 —— 纯色说明页面没渲染出来（构建失败/路径错误）
"""
import argparse
import sys

from PIL import Image
import numpy as np


def band_uniform(arr, tol):
    """返回 (是否均匀, 众数颜色, 偏离像素数)。"""
    flat = arr.reshape(-1, arr.shape[-1])
    colors, counts = np.unique(flat, axis=0, return_counts=True)
    mode = colors[counts.argmax()]
    dev = int((np.abs(flat.astype(int) - mode.astype(int)).max(axis=1) > tol).sum())
    return dev == 0, mode, dev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("--width", type=int, default=794)
    ap.add_argument("--page-height", type=int, default=1123)
    ap.add_argument("--margin", type=int, default=24)
    ap.add_argument("--tolerance", type=int, default=8, help="边距带允许的每通道色差")
    args = ap.parse_args()

    im = Image.open(args.png).convert("RGB")
    arr = np.asarray(im)
    h, w = arr.shape[:2]
    expect = (args.width, args.page_height + 2 * args.margin)
    fails = []

    if (w, h) != expect:
        fails.append(f"尺寸 {w}×{h} ≠ 预期 {expect[0]}×{expect[1]}")

    m, ph = args.margin, args.page_height
    if h >= 2 * m + 10:  # 尺寸异常时仍尽量检查
        top, bottom = arr[:m], arr[m + ph:] if m + ph < h else arr[-m:]
        for name, band in (("上边距", top), ("下边距", bottom)):
            if band.size == 0:
                continue
            ok, mode, dev = band_uniform(band, args.tolerance)
            if not ok:
                fails.append(f"{name}带不均匀：{dev} 个像素偏离底色 "
                             f"{tuple(int(x) for x in mode)} → 内容渗出页外")
        page = arr[m:m + ph]
        if page.size:
            ok, _, _ = band_uniform(page, args.tolerance)
            if ok:
                fails.append("页面区域为纯色 → 页面未渲染内容")
        last = arr[m + ph - 1]
        print(f"信息: 页面末行非背景像素 "
              f"{int((np.abs(last.astype(int) - last[0].astype(int)).max(axis=1) > args.tolerance).sum())}")

    if fails:
        print("❌ 预览验收未通过：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print(f"✅ 预览通过：{w}×{h}，边距干净，页面已渲染。")


if __name__ == "__main__":
    main()
