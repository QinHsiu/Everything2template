# e2t-oss-strongest-v4 结案（首轮）

**定位：** Apache-2.0 开源核心；目标是开源同类里**成稿效果最强**（可商用品质），不以付费墙为产品本体。

## 本轮修复

| 问题 | 处理 |
|------|------|
| 标题截断（`…：我用`） | `_theme_title` / titles `_theme` |
| 套话复读（先抓重点 / 别只收藏） | rewrite 重写 + validate `FILLER_SPAM` |
| 短段落误用无关 key_points | body 阈值降至 12，优先保留原文 |
| 质量不可度量 | `scripts/strongest_score.py` |

## 门禁

```bash
python scripts/strongest_score.py
# strongest_ready=true, quality_avg=100, tests pass
```

## 下一轮迭代候选（保持开源最强）

1. 平台深度：对齐 oh-my 转换 Skill 的更多开头/结尾变体（仍禁 cookie 发布）  
2. 更多对照样例：PDF / 代码项目 → 五平台 before-after  
3. 可选 LLM（DeepSeek/Ollama）作为增强，不作为开源默认依赖  
4. 平台数量：只在质量不掉的前提下加第 6+ 平台（宁深勿浅）
