import { Service, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { UploadApiService } from '../data-access/upload-api.service';
import type { GenerateUploadUrlsResponse } from '../data-access/upload-api.service';
import type { UploadState } from '../models/upload-state.model';

@Service()
export class UploadFacadeService {
  private readonly uploadApiService = inject(UploadApiService);

  async uploadFiles(files: File[], emitState: (state: UploadState) => void): Promise<void> {
    const totalFiles = files.length;

    if (totalFiles === 0) {
      return;
    }

    emitState({
      phase: 'requestingUrl',
      progress: null,
      totalFiles,
      uploadedFiles: 0,
      message: `Requesting secure upload URLs for ${totalFiles} files...`,
      error: null,
    });

    try {
      const response = await firstValueFrom<GenerateUploadUrlsResponse>(
        this.uploadApiService.generateUploadUrls(files.map((file) => file.type)),
      );

      if (response.uploads.length !== totalFiles) {
        throw new Error('UPLOAD_URL_COUNT_MISMATCH');
      }

      let uploadedFiles = 0;

      for (const [index, file] of files.entries()) {
        const presignedPost = response.uploads[index];

        emitState({
          phase: 'uploading',
          progress: Math.round((uploadedFiles / totalFiles) * 100),
          totalFiles,
          uploadedFiles,
          message: `Uploading image ${index + 1} of ${totalFiles}...`,
          error: null,
        });

        await this.uploadApiService.uploadFileToPresignedPost(presignedPost, file, (percent) => {
          const aggregateProgress = Math.round(
            ((uploadedFiles + percent / 100) / totalFiles) * 100,
          );

          emitState({
            phase: 'uploading',
            progress: aggregateProgress,
            totalFiles,
            uploadedFiles,
            message: `Uploading image ${index + 1} of ${totalFiles}...`,
            error: null,
          });
        });

        uploadedFiles += 1;
      }

      emitState({
        phase: 'success',
        progress: null,
        totalFiles,
        uploadedFiles: totalFiles,
        message: `Upload complete. ${totalFiles} image${totalFiles === 1 ? '' : 's'} submitted for review.`,
        error: null,
      });
    } catch (error: unknown) {
      emitState({
        phase: 'error',
        progress: null,
        totalFiles,
        uploadedFiles: 0,
        message: null,
        error: this.mapUploadError(error),
      });
    }
  }

  private mapUploadError(error: unknown): string {
    if (error instanceof Error && error.message === 'UPLOAD_ABORTED') {
      return 'Upload was canceled. Please try again.';
    }

    if (error instanceof Error && error.message === 'UPLOAD_URL_COUNT_MISMATCH') {
      return 'Upload initialization failed. Please try again.';
    }

    return 'Upload failed. Ensure every file is JPG or PNG, with at most 10 images, and try again.';
  }
}
