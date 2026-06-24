export type UploadPhase = 'idle' | 'requestingUrl' | 'uploading' | 'success' | 'error';

export interface UploadState {
  phase: UploadPhase;
  progress: number | null;
  totalFiles: number;
  uploadedFiles: number;
  message: string | null;
  error: string | null;
}

export const initialUploadState: UploadState = {
  phase: 'idle',
  progress: null,
  totalFiles: 0,
  uploadedFiles: 0,
  message: null,
  error: null,
};
