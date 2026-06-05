import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { UploadApiService } from '../data-access/upload-api.service';
import { UploadState } from '../models/upload-state.model';

@Injectable({
  providedIn: 'root',
})
export class UploadFacadeService {
  private readonly uploadApiService = inject(UploadApiService);

  async uploadFile(file: File, emitState: (state: UploadState) => void): Promise<void> {
    emitState({
      phase: 'requestingUrl',
      progress: null,
      message: 'Requesting secure upload URL...',
      error: null,
    });

    try {
      const presignedPost = await firstValueFrom(
        this.uploadApiService.generateUploadUrl(file.type),
      );

      emitState({
        phase: 'uploading',
        progress: 0,
        message: 'Uploading image to secure storage...',
        error: null,
      });

      await this.uploadApiService.uploadFileToPresignedPost(presignedPost, file, (percent) => {
        emitState({
          phase: 'uploading',
          progress: percent,
          message: 'Uploading image to secure storage...',
          error: null,
        });
      });

      emitState({
        phase: 'success',
        progress: null,
        message: `Upload complete. Image ID: ${presignedPost.image_id}`,
        error: null,
      });
    } catch (error: unknown) {
      emitState({
        phase: 'error',
        progress: null,
        message: null,
        error: this.mapUploadError(error),
      });
    }
  }

  private mapUploadError(error: unknown): string {
    if (error instanceof Error && error.message === 'UPLOAD_ABORTED') {
      return 'Upload was canceled. Please try again.';
    }

    return 'Upload failed. Ensure the image type is JPG or PNG and try again.';
  }
}
