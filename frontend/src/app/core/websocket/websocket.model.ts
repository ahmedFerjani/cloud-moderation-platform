export interface ModerationResultMessage {
  type: 'moderation_result';
  status: 'success' | 'rejected';
  imageId: string;
  moderationStatus?: 'safe' | 'unsafe';
  reason?: string;
}
