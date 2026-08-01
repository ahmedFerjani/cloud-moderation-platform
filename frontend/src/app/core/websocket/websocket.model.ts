export interface ModerationResultMessage {
  type: 'moderation_result';
  status: 'success' | 'rejected';
  imageId: string;
  reason?: string;
}
