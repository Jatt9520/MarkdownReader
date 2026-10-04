"""AI module tests: presets, prompts, settings storage. No network."""

from markdownreader.ai.presets import AI_PRESETS, PRESET_CUSTOM, build_prompt, has_cjk
from markdownreader.settings import Settings


def test_presets_are_openai_compatible():
    for name, preset in AI_PRESETS.items():
        assert preset["base"].startswith("http"), name
        assert preset["model"], name
        if not preset["base"].startswith("http://localhost"):
            assert preset["base"].startswith("https://"), name


def test_preset_custom_exists():
    assert PRESET_CUSTOM == "自定义"


def test_has_cjk():
    assert has_cjk("你好")
    assert has_cjk("plain テキスト")
    assert not has_cjk("plain text")


def test_polish_prompt_plain_output():
    system, user = build_prompt("polish", "选中的文字")
    assert "错别字" in system and "只输出" in system
    assert user == "选中的文字"


def test_translate_direction_auto():
    zh_system, _ = build_prompt("translate", "中文内容")
    en_system, _ = build_prompt("translate", "english content")
    assert "英文" in zh_system
    assert "中文" in en_system and "英文" not in en_system


def test_custom_prompt_carries_instruction():
    _, user = build_prompt("custom", "正文", custom="改成正式语气")
    assert "改成正式语气" in user and "正文" in user


def test_unknown_action_raises():
    try:
        build_prompt("nope", "x")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_ai_settings_roundtrip(settings):
    settings.ai_api_base = "https://api.deepseek.com/v1"
    settings.ai_api_key = "sk-test"
    settings.ai_model = "deepseek-chat"
    fresh = Settings()
    assert fresh.ai_api_base == "https://api.deepseek.com/v1"
    assert fresh.ai_api_key == "sk-test"
    assert fresh.ai_model == "deepseek-chat"
    assert fresh.ai_configured


def test_ai_not_configured_when_empty(settings):
    assert not settings.ai_configured
    settings.ai_api_base = "https://x/v1"
    assert not settings.ai_configured  # model still missing
    settings.ai_model = "m"
    assert settings.ai_configured
