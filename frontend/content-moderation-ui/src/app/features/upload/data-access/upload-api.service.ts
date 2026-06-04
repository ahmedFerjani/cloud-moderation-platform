import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

interface GenerateUploadUrlRequest {
  content_type: string;
}

interface GenerateUploadUrlResponse {
  upload_url: string;
  upload_method: 'POST';
  upload_form_fields: Record<string, string>;
  image_id: string;
  object_key: string;
  expires_in: number;
  max_upload_size_bytes: number;
}

@Injectable({
  providedIn: 'root',
})
export class UploadApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = environment.apiBaseUrl.replace(/\/$/, '');

  generateUploadUrl(contentType: string): Observable<GenerateUploadUrlResponse> {
    const payload: GenerateUploadUrlRequest = {
      content_type: contentType,
    };

    return this.http.post<GenerateUploadUrlResponse>(
      `${this.apiBaseUrl}/generate-upload-url`,
      payload
    );
  }

  async uploadFileToPresignedPost(
    presignedPost: GenerateUploadUrlResponse,
    file: File,
    onProgress?: (percent: number) => void,
  ): Promise<void> {
    const formData = new FormData();

    for (const [key, value] of Object.entries(presignedPost.upload_form_fields)) {
      formData.append(key, value);
    }

    formData.append('file', file, file.name);

    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.open('POST', presignedPost.upload_url);

      xhr.upload.onprogress = (event: ProgressEvent) => {
        if (!event.lengthComputable || !onProgress) {
          return;
        }

        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(Math.min(percent, 100));
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          onProgress?.(100);
          resolve();
          return;
        }

        reject(new Error('UPLOAD_FAILED'));
      };

      xhr.onerror = () => {
        reject(new Error('UPLOAD_FAILED'));
      };

      xhr.onabort = () => {
        reject(new Error('UPLOAD_ABORTED'));
      };

      xhr.send(formData);
    });
  }
}
