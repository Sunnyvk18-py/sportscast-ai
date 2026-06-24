"""PyTorch crowd noise classifier."""

import logging
import os
import time
from uuid import uuid4

from pipeline.audio.feature_extractor import AudioFeatureExtractor
from pipeline.audio.pretrained_weights import HeuristicCrowdClassifier
from pipeline.kafka.schemas import AudioEvent

logger = logging.getLogger(__name__)


class CrowdNoiseClassifier:
    def __init__(self, model_path: str | None = None):
        self.extractor = AudioFeatureExtractor()
        self.heuristic = HeuristicCrowdClassifier()
        self.model = None
        self.device = "cpu"
        self._model_path = model_path

        if model_path and os.path.isfile(model_path):
            try:
                import torch

                from pipeline.audio.model import CrowdNoiseModel

                self.model = CrowdNoiseModel()
                state = torch.load(model_path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(state)
                self.model.to(self.device)
                self.model.eval()
            except Exception as exc:
                logger.warning("Failed to load crowd model weights: %s", exc)
                self.model = None

    async def classify(self, audio_path: str, segment_id: str, timestamp_ms: int) -> AudioEvent:
        start = time.perf_counter()
        try:
            features = self.extractor.extract(audio_path)
            mfcc = features["mfcc"]
            energy = features["energy"]

            if self.model is not None:
                import torch

                from pipeline.audio.model import CrowdNoiseModel

                x = torch.tensor([mfcc + [energy]], dtype=torch.float32, device=self.device)
                with torch.no_grad():
                    probs = self.model(x)[0]
                idx = int(torch.argmax(probs).item())
                crowd_state = CrowdNoiseModel.CLASSES[idx]
                confidence = float(probs[idx].item())
            else:
                crowd_state, confidence = self.heuristic.classify(features)

            processing_ms = int((time.perf_counter() - start) * 1000)
            return AudioEvent(
                event_id=str(uuid4()),
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                energy_level=energy,
                crowd_state=crowd_state,
                classifier_confidence=confidence,
                mfcc_features=mfcc,
                processing_ms=processing_ms,
            )
        except Exception as exc:
            logger.warning("Audio classification failed: %s", exc)
            return AudioEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                energy_level=0.3,
                crowd_state="ambient",
                classifier_confidence=0.5,
                mfcc_features=[0.0] * 13,
                processing_ms=int((time.perf_counter() - start) * 1000),
            )
