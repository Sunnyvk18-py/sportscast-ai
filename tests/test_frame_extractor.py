"""Tests for frame extractor."""

from pipeline.vision.frame_extractor import FrameExtractor


def test_frame_to_base64(tmp_path):
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"\xff\xd8\xff")
    extractor = FrameExtractor()
    b64 = extractor.frame_to_base64(str(frame))
    assert len(b64) > 0
