# LLM 配置（DeepSeek / Ollama）

默认优先 **DeepSeek**；也可使用本机开源 **Ollama**（无需云端 Key）。

## DeepSeek

1. 打开 https://platform.deepseek.com/ 创建 API Key  
2. 在仓库根目录：

```bash
cd Everything2template
cp .env.example .env   # Windows: Copy-Item .env.example .env
# 编辑 .env：DEEPSEEK_API_KEY=sk-...
# 可选：E2T_LLM_PROVIDER=deepseek  或  auto
```

3. 验证：`python -m e2t llm-info` → `"configured": true`

## Ollama（开源本地）

1. 安装 https://ollama.com  
2. `ollama pull qwen2.5:7b`  
3. `.env`：

```text
E2T_LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_HOST=http://127.0.0.1:11434
```

4. `python -m e2t llm-info` 应显示 `provider: ollama`

`E2T_LLM_PROVIDER=auto` 时：有可用云端 Key 用云端，否则若 Ollama 在线则自动用 Ollama。

## 试用台

```bash
python -m e2t web --port 8767
```

勾选「启用 LLM 精修」；未配置时仍走规则改写引擎。
