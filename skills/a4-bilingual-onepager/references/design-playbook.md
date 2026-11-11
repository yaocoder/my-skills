# 设计手册：设计感四支柱（配色 · 排版 · 图示 · 美观）

配合 SKILL.md 第 5 步使用。所有配方均为**可直接粘贴的 CSS/SVG 片段**，颜色一律引用 `:root` 令牌（改色只改令牌，改完跑 `audit_contrast.py`）。
**铁律：任何设计改动都不得突破第 3 步高度预算——加图示、加装饰后必跑 `measure_layout.py`。**

---

## 1. 配色

### 1.1 色板骨架（每页五层，缺一层就容易「素」）

| 层 | 令牌/色值 | 用法 |
|---|---|---|
| 深蓝主系 | `--navy-ink #0B1F4F`、`--navy #1E40AF`、`--blue #2563EB` | Hero/CTA 对角渐变、区块标题、数字强调 |
| 浅色节奏带 | `--surface #F8FAFC`、`--tint #EEF2FF` | 相邻区块背景交替，破「白墙」 |
| 琥珀点睛 | 图形/色块 `#F59E0B`；白底文字 `#B45309`；深底文字 `#FBBF24`；浅底胶囊 `#FFF7E6`/边 `#FDE3B0` | 编号徽章、关键数字、CTA、金句下划线、徽标圆点 |
| 语义色 | 危险 `#EF4444` + 浅底 `#FEF2F2`；确认 `#059669` | 痛点图标方块、勾选项 |
| 中性文字四级 | `--strong #0F172A` → `--ink #334155` → `--mid #475569` → `--muted #64748B` | 标题→正文→说明→注释（对比度守则见 SKILL 第 4 步） |

### 1.2 节奏规则（防「素」的量化线）

- **每页视觉锚点 ≥3 个**：深色 Hero + ≥1 个图示面板 + ≥1 条浅色节奏带。
- **相邻区块背景交替**：白 → 浅带 → 图文 → 白；连续三块同底色 = 素。
- **琥珀出现 ≤5 处/页**（编号徽章、关键数字、CTA、金句下划线、徽标圆点），多于 5 处就廉价。
- **细线框 ≤6 处/页**：其余卡片用「1px 浅边 + 一档浅阴影」托底，别满页铁丝网。

### 1.3 配方

```css
/* Hero 对角渐变（配 .hero-grid 网格 + .hero-rings 取景环，见 3.8） */
.hero { background: linear-gradient(135deg, var(--navy-ink) 0%, var(--navy) 58%, #2563EB 100%); }

/* 浅色节奏带（信任条/任意区块） */
.band { background: linear-gradient(90deg, #F8FAFC 0%, #EEF2FF 100%); }

/* 琥珀编号徽章（区块标题统一用，见 2.2） */
.sec-head em { min-width: 19px; height: 19px; padding: 0 5px; border-radius: 5px;
  background: linear-gradient(135deg, #F59E0B, #D97706); color: #fff;
  font-size: 9.5px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(245,158,11,.35); }

/* 荣誉胶囊（白底上的琥珀 badge） */
.badge { color: var(--amber-text); font-weight: 600; background: #FFF7E6;
  border: 1px solid #FDE3B0; border-radius: 99px; padding: 3px 11px; }

/* CTA 渐变卡 + 右上光斑；卡内浅色文字对比度仍须 ≥4.5:1 */
.cta { background: linear-gradient(155deg, #2563EB 0%, var(--navy) 48%, var(--navy-deep) 100%); position: relative; overflow: hidden; }
.cta::after { content: ""; position: absolute; right: -46px; top: -56px; width: 170px; height: 170px;
  border-radius: 50%; background: radial-gradient(circle, rgba(56,189,248,.38), rgba(56,189,248,0) 70%); }
.cta > * { position: relative; }

/* 金句下划线（Hero 标题下的琥珀渐隐条） */
.hero-quote::after { content: ""; display: block; width: 136px; height: 4px; border-radius: 2px; margin-top: 7px;
  background: linear-gradient(90deg, #F59E0B, rgba(245,158,11,0)); }
```

---

## 2. 排版与组织

### 2.1 字号阶梯（A4 实测安全值，≥4 级）

| 层级 | 字号 | 字重 | 颜色 |
|---|---|---|---|
| 金句 hero-quote | 40px（zh）/ 32px（en） | 700 | 白 |
| 区块标题 sec-head b | 14px | 700 | `--navy` |
| 卡片标题 | 10–12px | 700 | `--strong` |
| 正文/要点 | 9–10px，行高 1.45–1.6 | 400/600 | `--ink`/`--mid` |
| 注释/注解 | 7.5–8.5px | 400 | `--muted` |
| 数字强调 stat | 15px | 700 | `--navy` |

规则：**相邻层级字号差 ≥2px 或字重差一档**；同一区块内字重最多两档；正文 <9px 只允许给三级注释，别把正文压到 7.5px。

### 2.2 区块标题统一模版（一个模子用到底）

```html
<div class="sec-head">
  <div class="t"><em>01</em><b>区块标题</b></div>
  <span>右侧灰色注解（一句话补充）</span>
</div>
```
```css
.sec-head { display: flex; justify-content: space-between; align-items: center; }
.sec-head .t { display: flex; align-items: center; gap: 9px; }
.sec-head em { /* 见 1.3 徽章配方 */ }
.sec-head b { font-size: 14px; color: var(--navy); font-weight: 700; }
.sec-head span { font-size: 9.5px; color: var(--mid); }
```
全页每个区块（含图示区）都用它——模子重复本身就是设计感。

### 2.3 信息组织方式选择

| 内容形态 | 组织方式 |
|---|---|
| 并列 3–4 项平级信息 | 卡片网格 / 多列面板（禁一排裸文字） |
| 有先后顺序 | 流程图（3.3） |
| 分层/归属关系 | 架构图（3.2） |
| 一组同属整体 | **单容器多列**——一个容器 = 一个整体的隐喻（3.5） |
| 段落式说明 | 每卡 ≤2 行，超了就该拆进图 |

间距只用一档节奏：区块上下 8–10px、卡片间距 8–10px、列间距 18px；同页不混用多套 gap。

---

## 3. 图示配方库（能画图的不用纯文字）

### 3.1 选型表

| 内容 | 图示 | 配方 |
|---|---|---|
| 分层架构（端/边/云/用…） | 层板面板 + 左侧流向轨 + 末端箭头 | 3.2 |
| 流程 / 闭环 | chevron 箭头块 + 虚线回流弧 | 3.3 |
| 价值链 / 演进关系 | 卡片 + 箭头串联 | 3.4 |
| 多角色 / 多维度并列 | 单容器多列面板 | 3.5 |
| 痛点 / 风险 | 浅底圆角图标方块 | 3.6 |
| 缺图 | 等尺寸占位框 | 3.7 |
| Hero 氛围 | 网格底纹 + 镜头取景环 | 3.8 |

### 3.2 分层架构图

```html
<div class="layers">
  <div class="layer"><div class="layer-chip l1">端</div><b>智能场景机 / AI 摄像头</b><span>现场感知</span>
    <svg class="layer-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="12" rx="2.5"/><circle cx="12" cy="13" r="3.2"/><path d="M8.5 7l1.2-2.2h4.6L15.5 7"/></svg></div>
  <!-- 边 / 云 / 用 同构 -->
</div>
```
```css
.layers { position: relative; display: flex; flex-direction: column; justify-content: center; gap: 6px;
  padding: 10px 14px; background: #fff; border: 1px solid var(--line);
  border-radius: 10px; box-shadow: var(--shadow); }
/* 流向轨：四层自上而下 */
.layers::before { content: ""; position: absolute; top: 26px; bottom: 26px; left: 27px; width: 2px;
  background: linear-gradient(180deg, #1E40AF, #0EA5E9); opacity: .45; }
/* 轨末端箭头 */
.layers::after { content: ""; position: absolute; bottom: 20px; left: 24px; width: 0; height: 0;
  border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-top: 6px solid rgba(2,119,179,.75); }
.layer { display: flex; align-items: center; gap: 10px; height: 22px; position: relative; }
.layer-chip { height: 20px; min-width: 26px; padding: 0 5px; border-radius: 5px; color: #fff; flex: none;
  font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 5px rgba(30,64,175,.25); }
.layer b { font-size: 10px; color: var(--strong); font-weight: 700; flex: none; }
.layer span { font-size: 9px; color: var(--mid); }
.layer .layer-ico { margin-left: auto; color: var(--muted); display: flex; flex: none; }
```
说明：中英两页轨位置不同时用 `.zh .layers::before { left: 27px } / .en … { left: 38px }` 覆盖（英文 chip 更宽）。

### 3.3 闭环流程图（chevron + 回流弧）

```html
<div class="steps">
  <div class="step"><span>1</span><b>发现问题</b></div>
  <div class="step"><span>2</span><b>即时告警</b></div>
  <div class="step"><span>3</span><b>派单到店</b></div>
  <div class="step"><span>4</span><b>现场整改</b></div>
  <div class="step"><span>5</span><b>验收考核</b></div>
</div>
<svg class="loop-back" viewBox="0 0 706 18" preserveAspectRatio="none" width="100%" height="18">
  <path d="M666 1 C666 12 652 15 353 15 C54 15 40 12 40 3" fill="none"
        stroke="#F59E0B" stroke-width="1.2" stroke-dasharray="5 5" opacity=".75"/>
  <path d="M40 0 l-4.5 8 l9 0 z" fill="#F59E0B" opacity=".9"/>
</svg>
```
```css
.steps { display: flex; align-items: stretch; margin-top: 8px; }
.step { flex: 1; height: 36px; margin-right: -7px; color: #fff;
  background: linear-gradient(135deg, #1E40AF, #2563EB);
  clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%, 12px 50%);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; }
.step:first-child { clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%); }
.step:last-child { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 12px 50%); margin-right: 0; }
.step:nth-child(even) { background: linear-gradient(135deg, #15307E, #1E40AF); } /* 深浅交替出节奏 */
.step span { font-size: 7.5px; font-weight: 700; color: rgba(255,255,255,.72); }
.step b { font-size: 10px; font-weight: 600; }
.loop-back { display: block; width: 100%; height: 18px; margin-top: 2px; }
```
要点：**回流弧是「闭环」二字的视觉证据**，从末步虚线绕回首步并带箭头，缺了它就只是直线流程。弧的 viewBox 宽度按内容区实际宽度写死（794−44×2=706），`preserveAspectRatio="none"` 在等宽下不畸变。

### 3.4 价值链箭头串联

```css
.chain { display: flex; align-items: stretch; }
.chain .card { flex: 1; /* 卡片样式同普通卡 */ box-shadow: var(--shadow); }
.chain-arrow { flex: none; width: 16px; display: flex; align-items: center; justify-content: center; color: #93C5FD; }
```
```html
<div class="chain">
  <div class="card">…</div>
  <div class="chain-arrow"><svg width="8" height="12" viewBox="0 0 8 12" fill="currentColor"><path d="M0 0l6 6-6 6z"/></svg></div>
  <div class="card">…</div> <!-- 重复 card + arrow -->
</div>
```

### 3.5 单容器多列面板（多角色/多维度）

```css
.panel { display: grid; grid-template-columns: repeat(4, 1fr);
  background: #fff; border: 1px solid var(--line); border-radius: 10px;
  box-shadow: var(--shadow); overflow: hidden; }
.panel .cell { display: flex; flex-direction: column; gap: 4px; padding: 8px 11px 9px;
  border-left: 1px solid var(--line-soft); }
.panel .cell:first-child { border-left: 0; }
```
设计语义：四列共处一框 = 「一套数据/一个平台」，比四张散卡多一层表达；列内 = 图标行（图标 + 名称 + 右贴标签）+ 一行说明。

### 3.6 图标方块与图标规范

```css
.ico-box { width: 26px; height: 26px; border-radius: 7px; flex: none;
  display: flex; align-items: center; justify-content: center; }
.ico-danger { background: #FEF2F2; }   /* 痛点：浅红底 + #EF4444 线性图标 */
.ico-tint   { background: var(--tint); } /* 中性：浅蓝底 + #1E40AF 线性图标 */
```
规范：**只用内联线性 SVG**（viewBox 24、stroke 1.5–1.8、圆头、14–16px），语义色对应（痛点红、价值卡用各自 bar 色、说明用 `--muted`）；**禁 emoji、禁多色位图图标**。

常用图标 path（stroke 即用）：

```html
<!-- 看不清/监控失效 --><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2z"/><circle cx="12" cy="12" r="3"/><path d="M3 3l18 18"/>
<!-- 管不住/锁定 --><rect x="4.5" y="10.5" width="15" height="9.5" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>
<!-- 算不清/下滑 --><path d="M4 6l6 6 4-4 6 6"/><path d="M20 10v6h-6"/>
<!-- 安全盾 --><path d="M12 3l7.5 2.8V12c0 4.6-3.2 7.4-7.5 8.5C7.7 19.4 4.5 16.6 4.5 12V5.8z"/>
<!-- 增长 --><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>
<!-- 运营/清单 --><rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 4.5V3.2h6V4.5"/><path d="M9 12.5l2 2 4-4"/>
<!-- 云 --><path d="M7.5 18.5a4.2 4.2 0 0 1 .6-8.4 5.6 5.6 0 0 1 10.7 1.3 3.6 3.6 0 0 1-.8 7.1z"/>
<!-- 摄像头 --><rect x="3" y="7" width="18" height="12" rx="2.5"/><circle cx="12" cy="13" r="3.2"/><path d="M8.5 7l1.2-2.2h4.6L15.5 7"/>
<!-- 边缘盒子 --><rect x="6.5" y="6.5" width="11" height="11" rx="1.5"/><path d="M10 2.5v4M14 2.5v4M10 17.5v4M14 17.5v4M2.5 10h4M2.5 14h4M17.5 10h4M17.5 14h4"/>
<!-- 总部大屏 --><rect x="2.5" y="4.5" width="19" height="12.5" rx="2"/><path d="M8.5 20.5h7M12 17v3.5"/>
<!-- 手机 --><rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10 18.5h4"/>
<!-- 门店 --><path d="M3.5 9.5 5 3.5h14l1.5 6"/><path d="M5 12v8.5h14V12"/><path d="M10 20.5V15h4v5.5"/>
```

### 3.7 占位框（生成不了的图片素材）

```html
<div class="ph" style="aspect-ratio:16/10">占位：门店驾驶舱截图</div>
```
```css
.ph { border: 1.5px dashed #93C5FD; border-radius: 8px; background: #F8FAFC;
  display: flex; align-items: center; justify-content: center;
  font-size: 8.5px; color: #64748B; letter-spacing: .05em; }
```
规则：**占位框必须与最终素材同尺寸/同比例**（避免补图时版面位移撑破预算）；占位文案写清素材内容与建议来源；补图后回第 3 步测高。别留白框——空白比占位更「素」。

### 3.8 Hero 氛围（网格底纹 + 镜头取景环）

```html
<div class="hero-grid"></div>
<svg class="hero-rings" width="300" height="300" viewBox="0 0 300 300" fill="none">
  <circle cx="150" cy="150" r="140" stroke="rgba(255,255,255,.14)"/>
  <circle cx="150" cy="150" r="104" stroke="rgba(255,255,255,.10)" stroke-dasharray="4 6"/>
  <circle cx="150" cy="150" r="66" stroke="rgba(255,255,255,.16)" stroke-width="1.5"/>
  <circle cx="150" cy="150" r="30" stroke="rgba(255,255,255,.20)"/>
  <path d="M150 0v24M150 276v24M0 150h24M276 150h24" stroke="rgba(255,255,255,.25)"/>
  <circle cx="150" cy="84" r="4" fill="#F59E0B"/>
</svg>
```
```css
.hero-grid { position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px);
  background-size: 26px 26px;
  -webkit-mask-image: radial-gradient(140% 110% at 88% -12%, #000 22%, transparent 70%);
  mask-image: radial-gradient(140% 110% at 88% -12%, #000 22%, transparent 70%); }
.hero-rings { position: absolute; right: -66px; top: -80px; pointer-events: none; }
```
结构要求：装饰元素放 Hero 内 **DOM 最前**，正文元素保持 `position: relative`——靠定位元素绘制顺序保证文字压在装饰之上，不需要 z-index。取景环点题「智慧视觉」，网格 mask 只在右上显影，透明度全部 ≤8%。

---

## 4. 美观细节令牌

```css
:root {
  --navy-ink: #0B1F4F; --navy-deep: #15307E;   /* 深蓝渐变两端 */
  --line-soft: #EDF2F9;                        /* 面板内分隔线（比 --line 更浅） */
  --shadow: 0 1px 3px rgba(15,23,42,.07), 0 1px 2px rgba(15,23,42,.05); /* 唯一一档阴影 */
}
```
- 圆角三档：6px（小徽章）/ 8px（卡片）/ 10px（面板、大卡），不混第四档。
- 渐变只用三处：Hero、CTA、编号徽章——到处渐变 = 没有渐变。
- 装饰纹理：透明度 ≤8%、绝对定位、mask 局部显影；打印已有 `print-color-adjust` 保护。
- 所有新颜色过 `audit_contrast.py`（文字）；装饰性色块不受对比度约束但别抢文字。

---

## 5. 设计评审清单（并入 SKILL 第 7 步循环，先于机械校验）

**缩略眯眼**（预览缩到 25% 整页看）：
- [ ] 三级层次一眼分明：金句 → 区块标题 → 正文
- [ ] 视觉锚点 ≥3（深色 Hero、图示面板、浅色节奏带），无连续三块同底色
- [ ] 至少 1 个真图示（架构/流程/串联之一），不是纯文字列表
- [ ] 琥珀点睛 ≤5 处，没有满页细线框

**定点放大**（4–5 处）：
- [ ] 所有区块标题同一模子（徽章 + 标题 + 注解）
- [ ] 图标风格统一（线性、同 stroke、同尺寸）、无 emoji
- [ ] 圆角/阴影/间距只用既定档位
- [ ] 无孤行标点、无文字贴边、无占位空框

**机械校验**（脚本，全 0 才算过）：
- [ ] `measure_layout.py`（图示吃高度，必跑）
- [ ] `verify_preview.py` ×2
- [ ] `audit_contrast.py`

**中英镜像**：同区块两页视觉等价（结构、锚点、图示一致，仅文案不同）。
