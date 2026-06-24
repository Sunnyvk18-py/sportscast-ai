export interface FusedEvent {
  event_id: string;
  timestamp_ms: number;
  segment_id: string;
  event_type: string;
  composite_confidence: number;
  signals_agreed: number;
  requires_review: boolean;
  auto_confirmed: boolean;
  commentary: string | null;
  highlight_clip_path: string | null;
  vision_signal?: {
    detected_event_type: string | null;
    confidence: number;
    model_used: string;
    processing_ms: number;
    frame_path?: string;
  } | null;
  speech_signal?: {
    transcript: string;
    detected_event_type: string | null;
    commentary_confidence: number;
    processing_ms: number;
  } | null;
  audio_signal?: {
    energy_level: number;
    crowd_state: string;
    classifier_confidence: number;
    mfcc_features: number[];
    processing_ms: number;
  } | null;
  created_at?: string;
}

export interface DetectedEvent {
  id: string;
  session_id: string;
  event_type: string;
  timestamp_ms: number;
  composite_confidence: number;
  signals_agreed: number;
  auto_confirmed: boolean;
  requires_review: boolean;
  commentary: string | null;
  highlight_clip_path: string | null;
  vision_confidence: number | null;
  speech_confidence: number | null;
  audio_energy: number | null;
  created_at: string;
}

export interface MatchSession {
  id: string;
  name: string;
  source_url: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  total_events: number;
}

export interface LiveMetrics {
  events_per_minute: number;
  avg_confidence: number;
  signal_agreement_rate: number;
  review_queue_depth: number;
  false_positive_rate_estimate: number;
  timestamp?: string;
}

export interface BenchmarkResult {
  total_clips: number;
  total_events_detected: number;
  precision: number;
  recall: number;
  f1_score: number;
  detection_latency_ms: number;
  false_positive_rate: number;
  signal_agreement_rate: number;
  per_event_type: Record<string, { tp: number; fp: number; fn: number }>;
}
