"""Secondary, optional LLM and Vision copilot bridge for clipboard input workflows."""

from __future__ import annotations

import base64
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from clipring.extract.screenshots import find_latest_image, get_default_screenshot_directory
from clipring.processors.chunker import move_last_line_to_top

# Default preset prompts preserved and modernized from legacy codebase
DEFAULT_PRESET_TEMPLATES = [
    (
        "If the input is a question, provide a detailed and direct answer. If it is arbitrary text, proofread and grammar-check it.",
        "Input:\n{q}",
    ),
    (
        "You are an expert software engineer and technical assistant. Answer the user's inquiry with precision and concise code examples where appropriate. Always place your final short conclusion in square brackets at the very end.",
        "Question:\n{q}",
    ),
    (
        "You are an expert technical tutor answering student inquiries. Format solutions clearly using plaintext. Conclude with your evaluation or final answer wrapped in square brackets on the final line.",
        "Problem:\n{q}",
    ),
]


class LLMBridge:
    """Optional bridge executing text and vision prompts over clipboard content."""

    def __init__(
        self,
        model: str = "gpt-4o",
        custom_provider: Optional[Callable[[str, Optional[str]], str]] = None,
        preset_index: int = 0,
    ) -> None:
        self.model = model
        self.custom_provider = custom_provider
        self.preset_index = preset_index
        self.presets = list(DEFAULT_PRESET_TEMPLATES)

    def format_prompt(self, user_text: str) -> tuple[str, str]:
        """Return (system_context, user_prompt) based on current preset."""
        idx = max(0, min(self.preset_index, len(self.presets) - 1))
        system_context, user_template = self.presets[idx]
        user_prompt = user_template.format(q=user_text)
        return system_context, user_prompt

    def ask(self, text: str, image_path: Optional[Path | str] = None) -> str:
        """Query LLM with text and optional image input."""
        context, prompt = self.format_prompt(text)
        img_str = str(image_path) if image_path else None

        # 1. Use custom provider if supplied
        if self.custom_provider is not None:
            raw = self.custom_provider(prompt, img_str)
            return move_last_line_to_top(raw)

        # 2. Default OpenAI provider (lazy import)
        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "OpenAI is required for the default AI bridge. Install it with: pip install clipring[ai]"
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        client = openai.OpenAI(api_key=api_key)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": context},
        ]

        if img_str and os.path.exists(img_str):
            with open(img_str, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                    ],
                }
            )
        else:
            messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        return move_last_line_to_top(content)

    def ask_latest_screenshot(self, query: str = "Explain what is in this image") -> str:
        """Find the latest screenshot and query the vision model."""
        screenshot_dir = get_default_screenshot_directory()
        latest = find_latest_image([screenshot_dir])
        if not latest:
            raise FileNotFoundError(f"No recent screenshots found in {screenshot_dir}")
        return self.ask(query, image_path=latest)
