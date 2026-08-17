export const MODERATION_RESULT_STATUSES = {
  SUCCESS: 'success',
  DUPLICATE: 'duplicate',
  REJECTED: 'rejected',
} as const;

export type ModerationResultStatus = 'success' | 'duplicate' | 'rejected';

export const MODERATION_STATUSES = {
  SAFE: 'safe',
  UNSAFE: 'unsafe',
} as const;

export type ModerationStatus = 'safe' | 'unsafe';

export interface ModerationResultMessage {
  type: 'moderation_result';
  status: ModerationResultStatus;
  imageId: string;
  fileName?: string;
  moderationStatus?: ModerationStatus;
  reason?: string;
}
