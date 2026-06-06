export interface ModerationLabel {
  ParentName: string;
  Confidence: number;
  Name: string;
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
  timestamp: string;
  status: ModerationStatus;
  s3_key: string;
}

export interface ModerationResultsResponse {
  items: ModerationResultItem[];
  count: number;
  last_evaluated_key: string | null;
}
