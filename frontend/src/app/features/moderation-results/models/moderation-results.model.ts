export interface ModerationLabel {
  ParentName: string;
  Confidence: number;
  Name: string;
}

export interface TextInsightToxicityLabel {
  name: string;
  score: number;
}

export interface TextInsightSentimentScores {
  Mixed: number;
  Neutral: number;
  Positive: number;
  Negative: number;
}

export interface TextInsights {
  sentiment_scores: TextInsightSentimentScores;
  toxicity_detected: boolean;
  language_code: string;
  pii_entities_count: number;
  toxicity_labels: TextInsightToxicityLabel[];
  max_toxicity_score: number;
  analyzed_text_length: number;
  sentiment: string;
  pii_entity_types: string[];
}

export interface ViewAccess {
  url: string;
  expires_in: number;
  issued_at: string;
}

export enum ModerationStatus {
  Safe = 'safe',
  Unsafe = 'unsafe',
}

export interface ModerationResultItem {
  unsafe_detected: boolean;
  image_hash: string;
  moderation_labels: ModerationLabel[];
  image_id: string;
  original_name?: string;
  timestamp: string;
  status: ModerationStatus;
  s3_key: string;
  text_insights?: TextInsights | null;
  view_access?: ViewAccess | null;
}

export interface ModerationResultViewAccessResponse {
  image_id: string;
  view_access: ViewAccess;
}

export interface ModerationResultsResponse {
  items: ModerationResultItem[];
  count: number;
  last_evaluated_key: Record<string, string> | null;
}
