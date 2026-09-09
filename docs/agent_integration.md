# AI & Agent Integration (Secondary Feature)

While ClipRing focuses primarily on being a high-performance **clipboard input mechanism**, it also includes an optional bridge for triggering LLM and vision completions directly from copied text and screenshots.

---

## 1. Installation

To enable AI features, install the optional `ai` dependencies:

```bash
pip install "clipring[ai]"
```

Set your API key in your environment or `.env` file:
```bash
export OPENAI_API_KEY="sk-..."
```

---

## 2. Using `LLMBridge`

`LLMBridge` provides model-agnostic prompting with vision capabilities and answer conclusion extraction.

```python
from clipring.ai.bridge import LLMBridge

bridge = LLMBridge(model="gpt-4o")

# 1. Text completion
answer = bridge.ask("Summarize the difference between asyncio and multiprocessing in Python.")
print(answer)

# 2. Vision completion on the latest screenshot
answer = bridge.ask_latest_screenshot("Explain any errors shown in this terminal screenshot.")
print(answer)
```

---

## 3. Creating a Clipboard Copilot

You can attach the bridge to a `ClipboardWatcher` to build an effortless background assistant:

```python
from clipring import ClipboardWatcher
from clipring.ai.bridge import LLMBridge
from clipring.core.models import ClipboardItem

bridge = LLMBridge(model="gpt-4o")
watcher = ClipboardWatcher(poll_interval=0.5)

@watcher.on_command(prefix=":ask")
def on_ask(item: ClipboardItem):
    prompt = (item.text or "").replace(":ask", "", 1).strip()
    if prompt:
        print(f"Processing inquiry: {prompt}")
        response = bridge.ask(prompt)
        # Push response back to clipboard for instant pasting
        watcher.clipboard.write_text(f":ans {response}")

watcher.run()
```

### Workflow
1. Select text in any application (browser, IDE, PDF reader).
2. Copy `:ask <your question>` to clipboard.
3. ClipRing intercepts the command, queries the model, and writes the response back to your clipboard.
4. Press `Ctrl+V` (or `Cmd+V`) to paste the answer.
