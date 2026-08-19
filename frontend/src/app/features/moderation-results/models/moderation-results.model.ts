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
}

export interface ModerationResultsResponse {
  items: ModerationResultItem[];
  count: number;
  last_evaluated_key: Record<string, string> | null;
}
