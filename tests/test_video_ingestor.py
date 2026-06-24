"""Tests for video ingestor."""

from unittest.mock import patch

import pytest

from pipeline.ingestor.video_ingestor import VideoIngestor


def test_local_file_returns_directly(tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake")
    ingestor = VideoIngestor(str(video), str(tmp_path))
    result = ingestor.download_video()
    assert result == str(video)


def test_download_missing_ytdlp(tmp_path):
    ingestor = VideoIngestor("https://example.com/video", str(tmp_path))
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            ingestor.download_video()
