"""Unit tests for LLMBridge prompt formatting and custom provider invocation."""

from clipring.ai.bridge import LLMBridge


def test_ai_bridge_custom_provider():
    def dummy_provider(prompt: str, image_path: str | None = None) -> str:
        return f"Processed: {prompt}\n[Approved]"

    bridge = LLMBridge(custom_provider=dummy_provider, preset_index=0)
    res = bridge.ask("Is this statement accurate?")
    # move_last_line_to_top should extract bracketed conclusion to top
    assert res.startswith("[Approved]")
    assert "Processed:" in res


def test_ai_bridge_format_prompt():
    bridge = LLMBridge(preset_index=1)
    context, prompt = bridge.format_prompt("How does asyncio work?")
    assert "expert software engineer" in context
    assert "How does asyncio work?" in prompt
