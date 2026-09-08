# VitePress config template

Put this at `docs/.vitepress/config.mts`. Replace titles, GitHub edit URL, and sidebar links with **this repo's** paths. Do not keep retail-specific page names.

```ts
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'PROJECT Wiki',
  description: '工程资料库（真相源：git docs/）',
  lang: 'zh-CN',
  base: '/',
  cleanUrls: true,
  lastUpdated: true,

  rewrites: {
    ':folder/README.md': ':folder/index.md',
    ':folder/:sub/README.md': ':folder/:sub/index.md',
  },

  ignoreDeadLinks: true,

  themeConfig: {
    outline: { label: '本页目录', level: [2, 3] },
    search: { provider: 'local' },
    socialLinks: [],
    editLink: {
      pattern: 'https://github.com/ORG/REPO/edit/BRANCH/docs/:path',
      text: '在 GitHub 编辑',
    },
    lastUpdated: { text: '最后更新' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    nav: [
      { text: '首页', link: '/' },
      { text: '维护规范', link: '/文档维护规范' },
    ],

    sidebar: [
      {
        text: '入门',
        collapsed: false,
        items: [
          { text: 'Wiki 首页', link: '/' },
          { text: '文档维护规范', link: '/文档维护规范' },
        ],
      },
      {
        text: '正式',
        collapsed: false,
        items: [
          { text: '文档索引', link: '/README' },
        ],
      },
      {
        text: '对外',
        collapsed: true,
        items: [],
      },
      {
        text: '过程',
        collapsed: true,
        items: [
          { text: 'Q&A', link: '/Q&A/' },
        ],
      },
    ],
  },
})
```

## Sidebar rules

- Link directory indexes as `/folder/` (README rewrite), not a random inner file unless that file **is** the landing page.
- Cap top-level sidebar at ~25 links. Deep pages are reachable from those indexes and search.
- After adding a canonical doc that belongs in nav, edit this config in the same PR as the Markdown.

## Root index vs README

- `docs/README.md` — GitHub / clone-first index
- `docs/index.md` — VitePress home (preview commands + three-layer table)

Do not rewrite `README.md` → `index.md` at the docs root when both files exist.
