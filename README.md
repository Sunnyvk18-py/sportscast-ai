# SportsCast AI

> Real-time multimodal sports event intelligence pipeline.
> Vision + Speech + Audio → Fused events → AI commentary → Highlight clips.

## Quickstart (no API keys)

```bash
git clone https://github.com/Sunnyvk18-py/sportscast-ai
cd sportscast-ai
pip install -e .
python examples/no_api_key_example.py
```

Output:

```
[00:08] FOUL         | Confidence: 82% | Signals: 3/3 | ✅ AUTO-CONFIRMED
  💬 Referee blows the whistle — that's a clear foul in midfield.

[00:23] CORNER       | Confidence: 71% | Signals: 2/3 | ✅ AUTO-CONFIRMED
  💬 Corner kick awarded, the winger races to place the ball.

[00:41] GOAL         | Confidence: 94% | Signals: 3/3 | ✅ AUTO-CONFIRMED
  💬 GOAL! The striker finds the back of the net!

[00:55] YELLOW_CARD  | Confidence: 58% | Signals: 2/3 | ⚠️  NEEDS REVIEW
  💬 Yellow card shown — the referee has made his decision.
```

## With real models

```bash
# Add to .env:
OPENAI_API_KEY=sk-...
USE_MOCK_PIPELINE=false
python examples/recorded_match_example.py --url "https://youtube.com/..."
```

## Dashboard

```bash
pip install -e ".[dashboard]"
docker-compose up
```

Open http://localhost:3000

## Architecture

```
Video Source (yt-dlp)
       │
       ▼
FFmpeg HLS Segmenter
       │
    ┌──┴──────────────────┐
    │                     │
    ▼                     ▼
Frame Extractor    Audio Extractor
    │                     │
    ▼                     ▼
Vision Detector    ┌──────┴──────┐
(GPT-4o/LLaVA)    │             │
    │         Whisper      Crowd Classifier
    │         Transcriber  (PyTorch)
    │              │             │
    └──────────────┼─────────────┘
                   │
             Kafka Topics
          (vision/speech/audio)
                   │
             Signal Fuser
          (timestamp alignment
           + confidence voting)
                   │
            ┌──────┴──────┐
            │             │
       Auto-Confirmed   Review Queue
            │         (human-in-loop)
            ▼
      LangGraph Agent
   (commentary + summary)
            │
      FFmpeg Clip Trim
            │
       Dashboard UI
```

## Signal Fusion Logic

An event fires when 2 of 3 signals agree within a 3-second window:

- Vision (45% weight): GPT-4o Vision frame analysis
- Speech (35% weight): Whisper transcript + keyword detection
- Audio (20% weight): PyTorch crowd noise classification

Confidence ≥ 75% → Auto-confirmed  
Confidence 45–75% → Human review queue  
Confidence < 45% → Discarded

## Supported Event Types

| Event | Vision Signal | Speech Keywords | Audio State |
|-------|--------------|-----------------|-------------|
| Goal | Net bulge / celebration | "goal", "scores" | Roar |
| Foul | Player down / whistle | "foul", "free kick" | Groan |
| Corner | Corner flag area | "corner kick" | Ambient |
| Yellow Card | Referee + yellow object | "yellow card", "booked" | Ambient |
| Red Card | Referee + red object | "red card", "sent off" | Ambient |
| Substitution | Players walking off | "coming on", "replaced" | Cheer |

## License

MIT
