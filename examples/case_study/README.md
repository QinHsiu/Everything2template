# Case study — before / after

Source: `examples/sample_inputs/demo_article.md` (generic long-form).

## Before (wrong)

Paste the same essay to 公众号 / 小红书 / 知乎 with light emoji changes.  
Result: platform algorithms and readers treat it as spammy cross-post.

## After (E2T)

```bash
e2t run examples/sample_inputs/demo_article.md --out-dir examples/case_study/run
```

| Platform | Artifact | What changed |
|----------|----------|--------------|
| WeChat | `run/wechat/draft.md` + `draft.wechat.html` | Hook + H2 + CTA + paste HTML |
| Xiaohongshu | `run/xiaohongshu/draft.md` | Keyword title + checklist + tags |
| Zhihu | `run/zhihu/draft.md` | Conclusion first + boundaries |
| Weibo | `run/weibo/draft.md` | Single sharp take |
| Douyin | `run/douyin/draft.md` | Shot-by-shot口播 |

Polished human-edited exemplars also live in `examples/sample_outputs/polished/`.

## Buyer takeaway

The product is **structure rebuild + export + gates**, not synonym spinning.
