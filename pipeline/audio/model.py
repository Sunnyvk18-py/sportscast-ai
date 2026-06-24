"""CrowdNoiseModel PyTorch architecture."""

import torch
import torch.nn as nn


class CrowdNoiseModel(nn.Module):
    CLASSES = ["roar", "cheer", "groan", "silence", "ambient"]

    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(14, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 5),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)
