from clipring.processors.chunker import TypewriterEcho, chunk_text, move_last_line_to_top
from fakes import FakeClipboardBackend


def test_chunk_text():
    text = "one two three four five six seven eight nine ten"
    chunks = chunk_text(text, max_chunk_size=15)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 15
    assert " ".join(chunks) == text


def test_move_last_line_to_top():
    response = "Line 1: explanation\nLine 2: calculation\n[Final Conclusion: 42]"
    rearranged = move_last_line_to_top(response)
    lines = rearranged.split("\n")
    assert lines[0] == "[Final Conclusion: 42]"
    assert lines[1] == "Line 1: explanation"


def test_typewriter_echo():
    fake_backend = FakeClipboardBackend()
    from clipring.core.manager import Clipboard

    cb = Clipboard(backend=fake_backend)
    echo = TypewriterEcho(clipboard=cb, delay=0.01)

    pushed = echo.echo("word1 word2 word3", delimiter="=", reverse=False)
    assert len(pushed) >= 1
    assert pushed[-1].endswith("=")
