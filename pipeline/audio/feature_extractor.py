"""librosa MFCC + energy feature extraction."""

import logging

logger = logging.getLogger(__name__)


class AudioFeatureExtractor:
    def extract(self, audio_path: str) -> dict:
        try:
            import librosa
            import numpy as np

            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            mfcc = librosa.feature.mfcc(y=y, sr=16000, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1).tolist()
            rms = librosa.feature.rms(y=y)[0]
            energy = float(np.mean(rms))
            energy_norm = min(1.0, energy * 10.0)
            duration_ms = int(len(y) / sr * 1000)
            return {"mfcc": mfcc_mean, "energy": energy_norm, "duration_ms": duration_ms}
        except Exception as exc:
            logger.warning("Audio feature extraction failed: %s", exc)
            return {
                "mfcc": [0.0] * 13,
                "energy": 0.3,
                "duration_ms": 0,
            }
