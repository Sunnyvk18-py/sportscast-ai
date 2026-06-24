"""Tests for audio classifier."""

import pytest

from pipeline.audio.pretrained_weights import HeuristicCrowdClassifier


def test_crowd_noise_model_forward():
    torch = pytest.importorskip("torch")
    from pipeline.audio.model import CrowdNoiseModel

    model = CrowdNoiseModel()
    x = torch.randn(1, 14)
    out = model(x)
    assert out.shape == (1, 5)
    assert torch.allclose(out.sum(dim=1), torch.ones(1), atol=1e-5)


def test_heuristic_classifier():
    clf = HeuristicCrowdClassifier()
    state, conf = clf.classify({"energy": 0.9})
    assert state == "roar"
    assert conf > 0.8
