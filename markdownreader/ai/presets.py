"""Provider presets and prompt builders for the AI assistant.

Any provider speaking the OpenAI chat-completions protocol works: the
user supplies a base URL, an API key, and a model name.
"""

import re

AI_PRESETS = {
    "OpenAI": {"base": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "DeepSeek": {"base": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "Kimi": {"base": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "智谱 GLM": {"base": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4-flash"},
    "通义千问": {"base": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"},
    "OpenRouter": {"base": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o-mini"},
    "Ollama (本地)": {"base": "http://localhost:11434/v1", "model": "qwen2.5", "key": "ollama"},
}

PRESET_CUSTOM = "自定义"

# (menu title, action id) in right-click order
ACTION_TITLES = [
    ("纠错润色", "polish"),
    ("翻译", "translate"),
    ("总结所选", "summarize"),
    ("解释这段", "explain"),
    ("续写", "continue"),
    ("自定义指令...", "custom"),
]

_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")


def has_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def build_prompt(action: str, text: str, custom: str | None = None) -> tuple[str, str]:
    """Return (system, user) prompts for an assistant action.

    Every prompt instructs the model to output plain result text only —
    the result is inserted into the document verbatim.
    """
    if action == "polish":
        return (
            "你是严谨的文字编辑。修复文本中的错别字、语病和标点问题，"
            "保持原意、语言与 Markdown 格式不变。"
            "只输出修改后的文本，不要解释，不要用代码块包裹。",
            text,
        )
    if action == "translate":
        target = "英文" if has_cjk(text) else "中文"
        return (
            f"你是专业翻译。把用户文本翻译成{target}，保持 Markdown 格式与结构。"
            "只输出译文，不要解释。",
            text,
        )
    if action == "summarize":
        return (
            "你是总结助手。把用户文本总结为不超过三句话的要点，"
            '输出为 Markdown 引用块（每行以 "> " 开头）。只输出引用块。',
            text,
        )
    if action == "explain":
        return (
            "你是耐心的讲解者。用简体中文解释用户给出的内容，"
            "先一句话概括再展开，简洁清晰。不要用代码块包裹整体回答。",
            text,
        )
    if action == "continue":
        return (
            "你是写作助手。阅读用户给出的 Markdown 文本结尾，自然地续写 1 到 2 段。"
            "保持语言、语气与格式一致，不要重复已有内容。只输出新增内容。",
            text,
        )
    if action == "custom":
        return (
            "你是 Markdown 写作助手。按照用户的指令处理提供的文本，"
            "只输出处理结果，不要解释，不要用代码块包裹。",
            f"指令：{custom}\n\n文本：\n{text}",
        )
    raise ValueError(f"unknown action: {action}")
