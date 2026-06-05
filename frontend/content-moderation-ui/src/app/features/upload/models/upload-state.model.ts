export type UploadPhase = 'idle' | 'requestingUrl' | 'uploading' | 'success' | 'error';

export interface UploadState {
  phase: UploadPhase;
  progress: number | null;
  message: string | null;
  error: string | null;
}

export const initialUploadState: UploadState = {
  phase: 'idle',
  progress: null,
  message: null,
  error: null,
};
