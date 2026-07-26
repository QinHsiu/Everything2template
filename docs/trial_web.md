# 试用网页

本地检验「是否达到可商业化效果」：

```bash
cd Everything2template
pip install -e .
e2t web --port 8767
```

浏览器打开：http://127.0.0.1:8767

## 怎么判

- 顶部效果分 ≥ **70**：当前素材下，骨架稿通过校验/合规，达到**可试用商业化门槛**
- 各平台页签里看：草稿结构是否平台原生、标题备选、配图计划、警告
- 骨架稿仍需 Agent/人工按 Skill 精修后才是发布终稿——试用台检验的是**管线与结构效果**，不是终稿文采

## API

- `GET /api/health`
- `GET /api/meta`
- `POST /api/convert` (multipart: source_text / source_url / upload / platforms)
