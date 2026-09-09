"""Example demonstrating secondary LLM copilot workflows using LLMBridge."""

import os
from clipring import ClipboardWatcher
from clipring.ai.bridge import LLMBridge
from clipring.core.models import ClipboardItem


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: Set OPENAI_API_KEY in your environment to run live LLM completions.")
        return

    bridge = LLMBridge(model="gpt-4o")
    watcher = ClipboardWatcher(poll_interval=0.5)

    print("Clipboard LLM Copilot Active:")
    print("  • Copy text starting with ':ask <prompt>' to query the model.")
    print("  • Copy ':img' to analyze the latest screenshot.")

    @watcher.on_command(prefix=":ask")
    def handle_ask(item: ClipboardItem) -> None:
        query = (item.text or "").replace(":ask", "", 1).strip()
        if not query:
            return
        print(f"Querying model: {query}")
        answer = bridge.ask(query)
        print(f"Answer received ({len(answer)} chars). Writing back to clipboard...")
        watcher.clipboard.write_text(f":ans {answer}")

    @watcher.on_command(command="img", prefix=":")
    def handle_image_query(item: ClipboardItem) -> None:
        print("Analyzing most recent screenshot...")
        try:
            answer = bridge.ask_latest_screenshot("Explain the code or visual details shown here.")
            watcher.clipboard.write_text(f":ans {answer}")
        except Exception as e:
            print(f"Error: {e}")

    watcher.run()


if __name__ == "__main__":
    main()
