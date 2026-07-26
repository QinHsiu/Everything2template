# Writer brief — douyin / mode=rewrite

## Instructions
1. Read the platform template rules carefully.
2. Use ONLY facts present in the CIR brief (do not invent metrics, quotes, or affiliations).
3. If a claim lacks evidence, mark it as 待核实 or omit it.
4. Output the final article in the template's required structure.
5. Voice profile / guidance:
Voice profile: Pro Operator (pro_operator)
Persona: 付费创作者顾问：强调可交付、可复盘、少承诺爆款
Do:
- 给清单
- 标出待核实
- 每篇一个主CTA
- 导出路径写清楚
Don't:
- 保证阅读量
- 编造客户案例
- 绝对化营销词
CTA overrides:
- wechat: 需要我按你的选题再出一版清单，评论「清单」。
- xiaohongshu: 要模板的扣「模板」，我发你结构框
- zhihu: 欢迎贴你的约束条件，我按约束改一版结论
- weibo: 转发给正在改稿崩溃的朋友
- douyin: 评论你的赛道，下期按赛道拆
Banned phrases: 10w+, 稳赚, 必火, 赋能

## Platform template
# 抖音口播脚本模板 / Douyin

## 目标

30–60 秒口播稿，含镜头提示。适合知识/工具类。

## 结构（必须）

```text
【封面文案】≤12 字

【0–3s 钩子】口头第一句（停滑）

【镜头1】画面：… / 口播：…
【镜头2】画面：… / 口播：…
【镜头3】画面：… / 口播：…

【结尾 CTA】关注 / 评论关键词

【BGM 建议】节奏感轻快 / 无 BGM
【字幕】关键词高亮 3–5 个
```

## 文风

- 完全口语，禁止书面长句
- 每 8–12 秒一个信息点
- 不承诺“必火/保量”

## format vs rewrite

- `format`：把要点改成口播句
- `rewrite`：重排钩子与节奏，不新增事实

## CIR brief
# demo_article
Source: markdown | examples\sample_inputs\demo_article.md

## Summary
# 把任何材料变成可发布内容：我用 Everything2template 做了一稿三发

## Key points
- 创作者最耗时间的不是「写」，而是「同一件事用三种平台语言再说一遍」。
- 公众号要有钩子和小节；小红书要关键词前置和步骤感；知乎要结论先行和边界条件。手动改三遍，质量还容易塌成「换皮粘贴」。
- ## 问题
- - 源材料形态太多：网页、PDF、文档、代码、整个项目
- ## 方法
- 1. 先把材料摄入成 CIR（Canonical Intermediate Representation）
- ## 结果

## Sections
### 把任何材料变成可发布内容：我用 Everything2template 做了一稿三发
创作者最耗时间的不是「写」，而是「同一件事用三种平台语言再说一遍」。

公众号要有钩子和小节；小红书要关键词前置和步骤感；知乎要结论先行和边界条件。手动改三遍，质量还容易塌成「换皮粘贴」。
### 问题
- 源材料形态太多：网页、PDF、文档、代码、整个项目
- 平台语风差异大，模板套用不等于平台原生
- 导出经常卡在「只能复制文本」，不便存档或对外交付
- 源材料形态太多：网页、PDF、文档、代码、整个项目
- 平台语风差异大，模板套用不等于平台原生
- 导出经常卡在「只能复制文本」，不便存档或对外交付
### 方法
1. 先把材料摄入成 CIR（Canonical Intermediate Representation）
2. 再按平台模板重写结构（不是同文换皮）
3. 用质量门禁检查套话、长度、CTA
4. 导出 Markdown / PDF
### 结果
你得到的是三份可继续精修的平台草稿 + 可交付文件，而不是一个「通用长文」。
### 边界
自动发布到平台后台、账号矩阵运营不属于本工具的默认范围；它专注「写对」与「导出」。

## Risks / caveats
- Heuristic CIR — agent should refine before publishing.

## Required deliverables
- Final article body (Markdown)
- 3 alternative titles
- Platform metadata block (tags/CTA/cover hints as required by template)
- Risks / assumptions list (short)