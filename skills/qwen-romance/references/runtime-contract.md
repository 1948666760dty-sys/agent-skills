# Qwen Romance Runtime Contract

本文件给 Skill Loader / 本地前端 / 自定义 Agent 使用。

## 1. 最小输入

Loader 在决定是否加载 `qwen-romance` 前，至少要得到：

```json
{
  "local": true,
  "provider": "local",
  "runtime": "ollama",
  "model_id": "qwen3:14b",
  "model_family": "qwen"
}
```

## 2. Gate

```python
def qwen_romance_gate(meta: dict, enabled: bool) -> bool:
    if not enabled:
        return False
    if meta.get("local") is not True:
        return False

    provider = str(meta.get("provider", "")).strip().lower()
    family = str(meta.get("model_family", "")).strip().lower()

    if provider == "openai":
        return False
    if family != "qwen":
        return False

    return True
```

如果无法取得可靠 `model_family`，返回 False。

## 3. 不要这样做

```python
# 错：所有本地模型都启用
return meta["local"]

# 错：OpenAI-compatible 就认为是 Qwen
return meta["api_style"] == "openai"

# 错：用户说是 Qwen 就相信
return user_text_contains("qwen")

# 错：配置可以覆盖 family
if enabled:
    return True
```

## 4. Prompt Composition

正确：

```text
detect model
→ gate
→ choose skill graph
→ compose prompt
```

错误：

```text
load all skills
→ compose giant prompt
→ tell non-Qwen to ignore Qwen Romance
```

GPT 路径的 Prompt 中不应出现本 Skill 正文。

## 5. 建议适配

- Ollama：读取实际 selected model / tags；项目侧登记 family=qwen。
- llama.cpp：读取模型 metadata / architecture / chat template；项目侧归一化为 family=qwen。
- LM Studio：读取实际 loaded model；不要因接口是 `/v1/chat/completions` 就认为 provider=OpenAI。
- 自定义 OpenAI-compatible 本地 API：`provider=local`，模型 family 单独判断。

## 6. Debug Contract

ACTIVE:

```json
{
  "skill": "qwen-romance",
  "gate": "ACTIVE",
  "reason": "local_qwen",
  "loaded": true
}
```

INACTIVE GPT:

```json
{
  "skill": "qwen-romance",
  "gate": "INACTIVE",
  "reason": "non_qwen_model",
  "loaded": false
}
```
