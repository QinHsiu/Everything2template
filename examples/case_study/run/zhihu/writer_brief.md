# Writer brief — zhihu / mode=rewrite

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
# 知乎模板 / Zhihu

## 目标

可信、可讨论的深度图文（文章或回答体）。推荐 1000–2500 字，开篇给结论。

## 结构（必须）

```text
# 标题（问题式或观点式，20–30 字）

**先说结论：** …

## 背景 / 问题定义
…

## 关键论证 1（含依据）
…

## 关键论证 2
…

## 反例或边界条件
…

## 总结
可执行建议 + 开放讨论邀请
```

## 标题公式

- `如何评价…？`
- `有哪些…的真相/方法？`
- `做了 N 年 …，我的结论是…`
- 避免夸张营销口吻；理性、可争议更好

另给 3 个备选标题。

## 文风

- 总–分–总；结论先行
- 用列表、小标题降低阅读成本
- 术语首次出现用一句人话解释
- 区分「事实（有出处）」与「观点（个人判断）」
- 代码/项目类内容可给最小复现步骤，但不要贴超长代码墙

## 元数据

- 话题标签 3–5 个
- 形态：`文章` 或 `回答`（若用户给的是问题，优先回答体）
- 是否适合知乎盐选/专栏：仅建议，不默认声称

## format vs rewrite

- `format`：保留论证链，补结论段与边界条件
- `rewrite`：可改叙事顺序与例证组织，不得伪造数据或经历

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