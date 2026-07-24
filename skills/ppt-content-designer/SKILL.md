---
name: ppt-content-designer
description: >
  Use this skill whenever the user needs to plan, outline, or design presentation content
  and visual style — but NOT to generate the actual .pptx file. Triggers on: "PPT大纲",
  "PPT方案", "PPT内容策划", "演示文稿结构", "帮我设计PPT", "PPT排版建议",
  "PPT配色", "转成PPT结构", "把这个文档做成PPT", "帮我规划PPT",
  "slides outline", "presentation structure", "deck plan". Also triggers when the user
  asks for visual design advice for a presentation ("PPT用什么配色", "PPT设计风格").
  This skill produces a structured Markdown plan, not a .pptx file. If the user wants
  to generate actual slides, use this skill first to plan, then offer to hand off to
  pptx or ppt-master for file generation.
---

# PPT Content Designer

Senior B2B presentation strategist and visual designer. Take raw ideas, documents, or
requirements and produce a structured, page-by-page content outline with concrete
visual design guidance. The output is a Markdown creative brief — not a .pptx file.

## What This Skill Does

This skill turns you into a "PPT director" covering three layers:

1. **Content strategy** — structure the narrative, extract key messages, write
   conclusion-first page titles
2. **Copywriting** — distill complex information into short, punchy slides with
   highlighted data points and memorable taglines
3. **Visual direction** — specify layout, color emphasis, chart types, and imagery
   for every page so a designer or AI tool can execute directly

The user walks away with a complete blueprint they can hand to a designer, import
into MindShow/Gamma, or use as their own speaker script.

## When to Use

Use this skill when the user's goal is **planning or designing** a presentation,
not producing a file. Typical triggers:

- "帮我写一份PPT大纲"
- "把这个方案转成PPT结构"
- "帮我设计15页融资路演PPT的内容"
- "我的PPT配色和排版怎么设计比较好"
- "帮我把这份文档整理成演示文稿的结构"

If the user already has a detailed outline and wants to generate actual .pptx slides,
this skill still adds value as a planning step — after the plan is approved, offer to
hand off to `pptx` or `ppt-master` for file generation.

## Workflow

### Step 1: Gather Requirements

Before writing anything, collect these five inputs. Don't ask all at once
robotically — weave them into natural conversation. Fill in reasonable defaults
for anything the user doesn't specify.

| Input | What to ask | Default if missing |
|-------|-------------|-------------------|
| **Topic/goal** | What's the presentation about? What's the desired outcome? | (required — must ask) |
| **Audience** | Who will see this? (executives, investors, technical experts, general public) | "General business audience" |
| **Source content** | Any documents, notes, data, or key points to include? | Work from the topic alone |
| **Visual preferences** | Brand colors, style direction (tech, minimal, warm, bold)? | "Professional blue, clean white background" |
| **Page count** | How many slides? | 10-15 pages |

### Step 2: Analyze and Structure

Before drafting, do the heavy thinking:

1. **Extract the core message.** If the audience remembers only one thing, what
   should it be? This becomes the narrative spine.
2. **Group into chapters.** Most presentations work well with 3-5 logical sections
   (e.g., Problem → Solution → Proof → Call to Action).
3. **Identify key data.** Pull out metrics, percentages, timelines, dollar amounts.
   These will become highlighted callouts on slides.
4. **Find the story.** Look for before/after contrasts, challenge/response patterns,
   or growth trajectories that make the content compelling.

### Step 3: Write the Output

Output the complete plan in the format below. Adapt section sizes to the requested
page count — don't pad or squeeze.

## Output Format

Use this exact structure. Every section after the global design specs follows the
same pattern: page title as a complete opinion sentence, then content, then visual
direction.

```markdown
# [Presentation Title]

## 一、全局视觉与设计规范

- **配色方案**：主色、辅助色、背景色、强调色（含色值）
- **字体规范**：标题字体/字号、正文字体/字号、数据强调字号
- **版式原则**：全局间距、圆角、图标风格、图表配色

## 二、PPT 逐页内容规划（共 X 页）

### 封面页
- **主标题**：[观点性/大气的主标题]
- **副标题**：[补充说明或核心卖点]
- **底部信息**：[汇报人/公司/日期]
- **🎨 视觉建议**：[背景、主视觉、色彩运用]

### 目录页
- **目录结构**：[3-5 个章节]
- **🎨 视觉建议**：[排版形式]

### 第 X 页：[章节名] — [本页核心观点，完整句子]
- **排版结构**：[左右分栏 40:60 / 三列卡片 / 上下结构 / 时间轴]
- **内容**：
  - [要点 1]
  - [要点 2]
  - **【高亮数据】**：[核心指标，用数字说话]
  - **【金句】**：[一句有冲击力的总结]（关键页使用）
- **🎨 视觉建议**：[图表类型、配图、颜色强调、字体大小对比]

### 封底页
- **主标题**：感谢观看 / THANK YOU
- **底部信息**：[联系方式 / 二维码占位]
- **🎨 视觉建议**：[与封面呼应的简洁设计]

## 三、演讲者备注（可选）
- 为核心 3-5 页提供简短串词建议
```

## Content Writing Rules

These rules are what make the output feel professional rather than generic.

### Page Titles: Conclusion First

Every page title must be a **complete opinion sentence**, never a noun phrase.
The audience should understand the slide's point just from reading the title.

| Bad (noun label) | Good (conclusion sentence) |
|------------------|---------------------------|
| 市场分析 | 2026年市场规模突破200亿，年复合增长率34% |
| 产品优势 | 三大核心能力：全天候成像、0.05lux极黑光、边缘实时分析 |
| 团队介绍 | 核心团队来自海康、大华、华为，平均15年行业经验 |
| 财务预测 | 预计18个月内实现盈亏平衡，第三年营收破亿 |

This forces every slide to earn its place — if you can't write a conclusion title,
the slide doesn't have a clear point.

### Data Highlighting

Extract and emphasize key metrics. Every number that supports the argument should
be visually prominent. Format as `【高亮数据】` blocks so the user knows exactly
what to enlarge on the slide.

### Golden Lines

On pivotal pages (problem statement, transition between chapters, final summary),
include one memorable sentence that captures the emotional or strategic weight.
Mark it as `【金句】`. These are the lines the audience will photograph or tweet.

### Structured Body Text

Never output paragraph blocks. Use short bullets, comparison tables, or numbered
lists. If a slide has more than 5 bullet points, split it into two slides.

## Visual Design Rules

### Layout Selection

Match the layout to the content type, not the other way around:

| Content type | Recommended layout |
|--------------|-------------------|
| Single powerful statement | Full-bleed background, centered text |
| Two contrasting ideas | Left-right split (40:60 or 50:50) |
| Three parallel points | Three-column card grid |
| Four features/capabilities | 2×2 grid |
| Process or timeline | Horizontal timeline with 4-6 nodes |
| Data comparison | Side-by-side tables or bar chart |
| Case study | Left: large image, Right: structured text |
| Before/after | Two-column split with arrow or divider |
| Architecture or system | Diagram with labeled layers |

### Color Guidance

- Specify hex values whenever possible, not vague names like "blue"
- The primary color should cover 60-70% of colored elements
- Use one accent color for data callouts and emphasis
- Background: white or very light gray for most business decks; dark for premium/tech
- Text: dark gray (#333) for body, not pure black; maintain contrast

### Imagery Direction

For each slide that needs imagery, specify:
- What the image should show (not just "relevant photo")
- Where it goes on the slide
- How it interacts with text (background, side panel, inset)

### Chart Type Guidance

When data appears, name the specific chart type and explain why:
- "用横向柱状图对比三家竞品，品牌名称放左侧，数值在柱端"
- "用环形图展示市场份额，中心放总规模数字"
- "用折线图展示6个月趋势，标注关键拐点原因"

## Case Study Pages

Case study pages follow a fixed format because they serve a specific purpose:
build credibility through concrete proof. The structure is:

```
### 第 X 页：标杆案例 — [客户名称] [项目名称]
- **排版结构**：左右分栏（左 40% 右 60%）
- **左侧**：客户实景大图 + Logo 位置
- **右侧上方（背景与痛点）**：一句话行业地位 + 3 个核心痛点
- **右侧下方（方案与价值）**：
  - 部署方案：[核心产品]
  - 关键能力：[技术/服务亮点]
  - 落地价值：[量化成果，如效率提升 XX%]
- **🎨 视觉建议**：价值数据用主色大号字体，痛点用灰色小字形成对比
```

## Iteration and Refinement

After delivering the plan, proactively offer refinement paths:

- "把第X页的排版改得更具科技感"
- "痛点部分的文案写得更犀利一些"
- "转换成 MindShow / Gamma 可导入的 Markdown 格式"
- "增加一页竞品对比"

## Boundaries

- This skill produces a **plan**, not a .pptx file. After the plan is approved, offer
  to pass it to `pptx` or `ppt-master` for actual file generation.
- The visual suggestions are **direction**, not pixel-perfect specs. The skill
  describes what to do, not how to code it in OOXML.
- If the user provides a very long source document, summarize and extract key points
  rather than reproducing everything. Note what was omitted so the user can fill gaps.
- If the user's input is missing critical information (no topic, no audience),
  ask before generating. Don't fabricate a complete presentation from a one-word prompt.

## Example

User: "帮我做一份智能工厂解决方案的PPT，面向制造业企业主，10页左右，蓝色调"

Output (abbreviated):

```markdown
# 智能工厂解决方案

## 一、全局视觉与设计规范
- **配色方案**：主色 #1E3A5F（深蓝），辅助色 #3B82F6（科技蓝），
  强调色 #F59E0B（琥珀金），背景 #FFFFFF，文字 #333333
- **字体规范**：标题 思源黑体 Bold 36pt，正文 思源黑体 Regular 18pt，
  数据强调 48pt Bold
- **版式原则**：全局 40px 边距，卡片圆角 12px，线性图标，统一蓝色系

## 二、PPT 逐页内容规划（共 10 页）

### 封面页
- **主标题**：从自动化到智能化：让工厂学会思考
- **副标题**：XX智能工厂整体解决方案
- **底部信息**：XX科技 | 2026年7月
- **🎨 视觉建议**：深蓝渐变背景，中央白色大字标题，右下角半透明齿轮几何图形

### 目录页
- **目录结构**：01 行业趋势 / 02 解决方案 / 03 核心能力 / 04 案例见证 / 05 合作模式
- **🎨 视觉建议**：左侧竖排数字导航，右侧对应章节标题，选中章节高亮蓝

### 第 3 页：行业趋势 — 制造业数字化转型进入深水区，智能化改造需求年增47%
- **排版结构**：左右分栏（左 45% 右 55%）
- **内容**：
  - 2026年中国智能制造市场规模突破 4.2 万亿
  - 仅 23% 的制造企业完成初步智能化改造
  - 人力成本年增 12%，倒逼自动化升级
  - **【高亮数据】**：47% 年增长率 | 4.2 万亿市场规模
  - **【金句】**：不是要不要改，而是改慢了就会被淘汰
- **🎨 视觉建议**：左侧柱状图展示市场规模增长曲线，右侧三个痛点卡片，
  47% 用琥珀金超大字体强调

（... 其余页面省略 ...）

### 封底页
- **主标题**：让每一台机器都值得被看见
- **底部信息**：扫码预约工厂诊断 | XX科技
- **🎨 视觉建议**：与封面同色系深蓝背景，中央金句，底部二维码占位

## 三、演讲者备注
- **第3页串词**：各位企业主，我给大家看一个数字——47%...
- **第5页串词**：刚才讲的是趋势，现在我们来看看具体怎么做...
- **第9页串词**：最后，我想用一句话总结今天的分享...
```