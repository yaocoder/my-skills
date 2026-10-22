# -*- coding: utf-8 -*-
"""minimal_deck — pptx-pipeline 技能包最小可运行示例。

演示本技能的正确姿势：**项目自定设计系统 + 中性工具库**——
色板常量与页面骨架函数写在项目脚本里，kit 只提供零预设的技术函数。

生成 3 页：封面 + 三卡结论页 + 原生流程图页，并做禁用词自检。
运行: python3 minimal_deck.py   （输出 minimal_deck.pptx）
渲染目检: python3 ../scripts/render_check.py minimal_deck.pptx --out ./pages
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import pptx_kit as K                       # noqa: E402
from pptx_kit import (new_deck, txbox, para, rect, hairline, dashed,   # noqa: E402
                      arrow_shape, blank)
from pptx.util import Pt                    # noqa: E402
from pptx.dml.color import RGBColor        # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR   # noqa: E402
from pptx.enum.shapes import MSO_SHAPE      # noqa: E402

# ============================================================
# 项目设计系统（示例值：本项目临时指定；真实项目应来自
# 内容文稿的「全局视觉与设计规范」章节或用户 VI）
# ============================================================
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREEN  = RGBColor(0x2C, 0x6E, 0x49)   # 主色
GREEN_D = RGBColor(0x1E, 0x4D, 0x32)  # 主色深阶
ACCENT = RGBColor(0xE0, 0x9F, 0x3E)   # 辅助色
GRAY   = RGBColor(0x8A, 0x85, 0x80)
BG     = RGBColor(0xFA, 0xF8, 0xF4)   # 页面底
ZEBRA  = RGBColor(0xF0, 0xEE, 0xE8)   # 斑马纹/chip 底
BORDER = RGBColor(0xD8, 0xD2, 0xC6)   # 卡片描边
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
DARKBG = RGBColor(0x14, 0x16, 0x12)   # 封面/封底底
PAPER_TX = RGBColor(0xEC, 0xEF, 0xE8)
CJK, NUM = "PingFang SC", "Georgia"

# 声明项目中文字体（kit 据此设置 a:ea，必须先于一切 para/chip 调用）
K.configure(cjk=CJK)

SW, SH, ML, MR, CW = K.SW, K.SH, K.ML, K.MR, K.CW

# ---------- 本项目页面骨架（内容页统一结构） ----------
def page(prs, kicker, title, page_no=None, quote=None):
    s = blank(prs, BG)
    tf = txbox(s, ML, 0.46, CW - 1.0, 0.3)
    para(tf, kicker, 9, GRAY, first=True, spc=200)
    tf = txbox(s, ML, 0.72, CW - 1.2, 0.52)
    para(tf, title, 20, GREEN, bold=True, first=True, line=1.0)
    hairline(s, ML, 1.34, CW, ACCENT)
    if page_no is not None:
        tf = txbox(s, SW - MR - 1.2, SH - 0.42, 1.2, 0.25)
        para(tf, f"{page_no:02d}", 9, GRAY, font=NUM, align=PP_ALIGN.RIGHT, first=True)
    if quote:
        rect(s, ML, SH - 0.89, 0.045, 0.26, fill=ACCENT)
        tf = txbox(s, ML + 0.16, SH - 0.92, CW - 0.4, 0.34)
        para(tf, quote, 11.5, INK, bold=True, first=True, line=1.1)
    return s


OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minimal_deck.pptx")
prs = new_deck()

# ---------- 第 1 页 · 封面 ----------
s = blank(prs, DARKBG)
rect(s, 0.95, 1.02, 0.55, 0.028, fill=ACCENT)
tf = txbox(s, 0.95, 1.14, 6.0, 0.3)
para(tf, "内部 · 战略汇报", 10.5, ACCENT, first=True, spc=300)
tf = txbox(s, 0.95, 1.8, 11.0, 1.4)
para(tf, "把结论放在第一页", 40, WHITE, bold=True, first=True, line=1.15)
tf = txbox(s, 0.95, 3.3, 9.0, 0.6)
para(tf, "副标题：结论先行 · 一页一判断 · 原生图形画图", 16, PAPER_TX, first=True)
bx = 0.95
for col, label in ((GREEN, "主色"), (ACCENT, "辅助色"), (GRAY, "中性色")):
    rect(s, bx, 6.28, 1.55, 0.075, fill=col)
    tf = txbox(s, bx, 6.46, 2.1, 0.3)
    para(tf, label, 9.5, PAPER_TX, first=True)
    bx += 2.35

# ---------- 第 2 页 · 三卡结论 ----------
s = page(prs, "EXAMPLE", "三张卡讲清一件事：结构与本项目设计系统一致", 1,
         quote=[("先定设计系统，", INK, True), ("再写版面", ACCENT, True), ("。", INK, True)])
cards = [("第一", "色板常量定义在项目脚本头部"),
         ("第二", "骨架函数 page() 由项目自建"),
         ("第三", "kit 只提供中性技术工具")]
cx = ML
for t, d in cards:
    rect(s, cx, 1.7, 3.9, 3.2, fill=WHITE, line=BORDER, rounded=True)
    tf = txbox(s, cx + 0.3, 2.0, 3.3, 0.4)
    para(tf, t, 14, GREEN, bold=True, first=True)
    rect(s, cx + 0.3, 2.5, 0.42, 0.028, fill=ACCENT)
    tf = txbox(s, cx + 0.3, 2.72, 3.3, 1.6)
    para(tf, d, 11, INK, first=True, line=1.35)
    cx += 4.14

# ---------- 第 3 页 · 原生流程图 ----------
s = page(prs, "EXAMPLE", "流程图用原生形状：可编辑、可配色、可缩放", 2)
steps = [("采集", WHITE, INK), ("分析", WHITE, INK), ("结论", GREEN, WHITE)]
sx = ML
for i, (t, fill, tc) in enumerate(steps):
    shp = rect(s, sx, 2.2, 3.0, 1.0, fill=fill,
               line=None if fill == GREEN else BORDER, rounded=True)
    tf = shp.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, f"{i+1}. {t}", 13, tc, bold=True, align=PP_ALIGN.CENTER, first=True)
    if i < 2:
        arrow_shape(s, sx + 3.1, 2.5, 0.6, 0.4, ACCENT)
    sx += 3.7
dashed(s, ML + 9.4, 3.5, ML + 1.5, 3.5, GRAY, 1.0, arrow=True)
tf = txbox(s, ML, 3.62, CW, 0.3)
para(tf, "虚线表示回流：结论反哺下一轮采集", 9.5, GRAY, align=PP_ALIGN.CENTER, first=True)

prs.save(OUT)
K.selfcheck(OUT, banned=("禁用词示例",))
print("saved:", OUT)
