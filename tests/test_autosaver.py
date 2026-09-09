from clipring.core.models import ClipboardItem, ContentType
from clipring.processors.autosaver import AutoSaver
from fakes import FakeClipboardBackend


def test_autosaver_save_image(tmp_path, sample_image_payload):
    fake_backend = FakeClipboardBackend()
    saver = AutoSaver(save_dir=tmp_path, notify_on_save=False, backend=fake_backend)

    item = ClipboardItem(
        content_type=ContentType.IMAGE,
        image=sample_image_payload,
    )

    saved_path = saver.process_item(item)
    assert saved_path is not None
    assert saved_path.exists()
    assert saved_path.suffix.lower() == ".png"
    assert saved_path.parent == tmp_path

    # Immediate second save of identical image should be deduplicated
    saved_second = saver.process_item(item)
    assert saved_second is None


def test_autosaver_copy_file(tmp_path):
    fake_backend = FakeClipboardBackend()
    saver = AutoSaver(save_dir=tmp_path / "out", notify_on_save=False, backend=fake_backend)

    src_file = tmp_path / "source.jpg"
    src_file.write_bytes(b"dummy_image_data_jpg")

    item = ClipboardItem(
        content_type=ContentType.FILES,
        files=[src_file],
    )

    saved = saver.process_item(item)
    assert saved is not None
    assert saved.exists()
    assert saved.name.endswith(".jpg")
    assert saved.read_bytes() == b"dummy_image_data_jpg"
