import io
import zipfile

from app.routers.export import _unique_filenames


def test_unique_filenames_dedupes_repeats():
    result = _unique_filenames(["IMG_0001.jpg", "IMG_0002.jpg", "IMG_0001.jpg", "IMG_0001.jpg"])
    assert result == ["IMG_0001.jpg", "IMG_0002.jpg", "IMG_0001 (1).jpg", "IMG_0001 (2).jpg"]


def test_unique_filenames_handles_no_extension():
    result = _unique_filenames(["photo", "photo"])
    assert result == ["photo", "photo (1)"]


def test_zip_roundtrip_preserves_original_bytes(tmp_path):
    """Sanity check that zipping+reading back a file gives identical bytes
    — the export endpoint should never re-encode or touch photo content."""
    original = tmp_path / "test.jpg"
    original.write_bytes(b"not a real jpeg, just bytes to check integrity")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(original, arcname="test.jpg")
    buffer.seek(0)

    with zipfile.ZipFile(buffer) as zf:
        assert zf.read("test.jpg") == original.read_bytes()
