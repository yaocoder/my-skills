# my-skills

AionUI / OpenCode 自定义技能仓库。

## 技能列表

| 技能 | 描述 |
|------|------|
| [ppt-content-designer](./skills/ppt-content-designer/) | PPT 内容策划与设计规范生成器。将原始需求/文档转化为逐页内容大纲 + 视觉设计指引 |
| [uat-tester](./skills/uat-tester/) | 通用用户验收（UAT）测试体系执行器，框架无关、项目无关。先文档化角色矩阵与追溯矩阵，再落地自动化脚本（Playwright/WebdriverIO/Appium/Detox）。内建四条防回归原则：首屏零噪音、深链接抽屉覆盖、数据范围按角色隔离、幂等造数与隔离 |

## 安装

### 安装单个技能

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills/ppt-content-designer"}
JSON
```

### 安装全部技能

```bash
git clone --depth 1 https://github.com/yaocoder/my-skills.git /tmp/my-skills
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills"}
JSON
```

安装后记得将技能绑定到对应助手：

```bash
# 查看当前助手名称
"$AIONUI_HELPER_BIN" config assistants list

# 绑定技能（替换 <助手ID> 为实际 ID）
"$AIONUI_HELPER_BIN" config assistants update <<'JSON'
{
  "assistant_id": "<助手ID>",
  "enabled_skills": ["ppt-content-designer"]
}
JSON
```

> ⚠️ 技能绑定后仅对新会话生效，当前正在进行的会话不会自动加载。

## 更新

```bash
cd /tmp/my-skills && git pull
# 重新导入（会覆盖更新）
"$AIONUI_HELPER_BIN" config skills import <<'JSON'
{"skill_path": "/tmp/my-skills/skills/ppt-content-designer"}
JSON
```

## 添加新技能

1. 在 `skills/` 下创建子目录：`mkdir -p skills/<技能名>`
2. 放入 `SKILL.md` 文件
3. 提交推送：

```bash
git add skills/<技能名> && git commit -m "feat: add <技能名> skill" && git push
```

## 技能结构要求

```
skills/
└── <技能名>/
    └── SKILL.md    # 技能定义文件（YAML frontmatter + Markdown 内容）
```

`SKILL.md` 需包含 YAML frontmatter，定义技能名称和描述：

```yaml
---
name: <技能名>
description: >
  技能描述，说明何时触发该技能
---
```

## 相关资源

- [AionUI](https://aionui.com)
