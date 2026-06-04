import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { firstValueFrom } from 'rxjs';
import { UploadApiService } from '../../data-access/upload-api.service';

@Component({
  selector: 'app-upload-page',
  imports: [MatCardModule, MatButtonModule, MatIconModule, MatProgressBarModule],
  templateUrl: './upload-page.component.html',
  styleUrl: './upload-page.component.scss',
})
export class UploadPageComponent {
  private readonly uploadApiService = inject(UploadApiService);

  protected readonly isDragActive = signal(false);
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly selectedFileName = signal<string | null>(null);
  protected readonly selectedFileSizeBytes = signal<number | null>(null);
  protected readonly selectedFilePreviewUrl = signal<string | null>(null);
  protected readonly isUploading = signal(false);
  protected readonly uploadProgressPercent = signal<number | null>(null);
  protected readonly uploadStatusMessage = signal<string | null>(null);
  protected readonly uploadErrorMessage = signal<string | null>(null);
  protected readonly selectedFileSizeLabel = computed(() => {
    const size = this.selectedFileSizeBytes();
    if (size === null) {
      return null;
    }

    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  });

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.setSelectedFile(file);
  }

  protected onPickerDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragActive.set(true);
  }

  protected onPickerDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragActive.set(false);
  }

  protected onPickerDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragActive.set(false);
    const file = event.dataTransfer?.files?.[0] ?? null;
    this.setSelectedFile(file);
  }

  protected clearSelectedFile(fileInput: HTMLInputElement): void {
    fileInput.value = '';
    this.setSelectedFile(null);
  }

  protected async onUpload(): Promise<void> {
    const file = this.selectedFile();
    if (!file || this.isUploading()) {
      return;
    }

    this.uploadErrorMessage.set(null);
    this.uploadProgressPercent.set(null);
    this.uploadStatusMessage.set('Requesting secure upload URL...');
    this.isUploading.set(true);

    try {
      const presignedPost = await firstValueFrom(
        this.uploadApiService.generateUploadUrl(file.type),
      );

      this.uploadStatusMessage.set('Uploading image to secure storage...');
      this.uploadProgressPercent.set(0);
      await this.uploadApiService.uploadFileToPresignedPost(presignedPost, file, (percent) => {
        this.uploadProgressPercent.set(percent);
      });

      this.uploadStatusMessage.set(`Upload complete. Image ID: ${presignedPost.image_id}`);
    } catch {
      this.uploadStatusMessage.set(null);
      this.uploadErrorMessage.set(
        'Upload failed. Ensure the image type is JPG or PNG and try again.',
      );
    } finally {
      this.isUploading.set(false);
      this.uploadProgressPercent.set(null);
    }
  }

  private setSelectedFile(file: File | null): void {
    const currentPreviewUrl = this.selectedFilePreviewUrl();
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }

    this.selectedFile.set(file);
    this.selectedFileName.set(file?.name ?? null);
    this.selectedFileSizeBytes.set(file?.size ?? null);
    this.selectedFilePreviewUrl.set(file ? URL.createObjectURL(file) : null);
    this.uploadProgressPercent.set(null);
    this.uploadStatusMessage.set(null);
    this.uploadErrorMessage.set(null);
  }
}
