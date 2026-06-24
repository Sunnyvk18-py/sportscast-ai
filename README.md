# SportsCast AI

> Real-time multimodal sports event intelligence pipeline.
> Vision + Speech + Audio → Fused events → AI commentary → Highlight clips.

## Quickstart

```bash
git clone https://github.com/Sunnyvk18-py/sportscast-ai
cd sportscast-ai
pip install -e ".[dashboard,speech]"

# Add to .env:
# OPENAI_API_KEY=sk-...

# Optional: start dashboard
docker compose up -d

# Process a YouTube link, stream, or local video file
python examples/live_stream_example.py --url "https://youtube.com/watch?v=..."
```

Requires **FFmpeg** on your PATH. Set `OPENAI_API_KEY` for GPT-4o Vision and Whisper API. For local Whisper: `pip install -e ".[speech]"`.

## Dashboard

```bash
pip install -e ".[dashboard]"
docker compose up
```

Open http://localhost:3000 — events appear live as the pipeline runs.

## CLI

```bash
python -m pipeline --url "https://youtube.com/watch?v=..."
python examples/recorded_match_example.py --url "/path/to/match.mp4"
```

Flags: `--no-dashboard`, `--no-clips`, `--name "My Match"`

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
