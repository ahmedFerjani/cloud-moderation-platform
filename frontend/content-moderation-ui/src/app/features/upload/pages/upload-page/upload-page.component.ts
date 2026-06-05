import { Component, computed, effect, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { SelectedFilePreviewComponent } from '../../components/selected-file-preview/selected-file-preview.component';
import { UploadFeedbackComponent } from '../../components/upload-feedback/upload-feedback.component';
import { UploadPickerComponent } from '../../components/upload-picker/upload-picker.component';
import { UploadFacadeService } from '../../facades/upload-facade.service';
import { UploadState, initialUploadState } from '../../models/upload-state.model';

@Component({
  selector: 'app-upload-page',
  host: {
    class: 'block',
  },
  imports: [
    MatCardModule,
    MatButtonModule,
    UploadPickerComponent,
    SelectedFilePreviewComponent,
    UploadFeedbackComponent,
  ],
  templateUrl: './upload-page.component.html',
})
export class UploadPageComponent {
  private readonly uploadFacadeService = inject(UploadFacadeService);

  protected readonly selectedFile = signal<File | null>(null);
  protected readonly selectedFilePreviewUrl = signal<string | null>(null);
  protected readonly selectedFileName = computed(() => this.selectedFile()?.name ?? null);
  protected readonly selectedFileSizeBytes = computed(() => this.selectedFile()?.size ?? null);
  protected readonly uploadState = signal<UploadState>(initialUploadState);
  protected readonly isUploading = computed(() => {
    const phase = this.uploadState().phase;
    return phase === 'requestingUrl' || phase === 'uploading';
  });
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

  constructor() {
    effect((onCleanup) => {
      const file = this.selectedFile();
      if (!file) {
        this.selectedFilePreviewUrl.set(null);
        return;
      }

      const previewUrl = URL.createObjectURL(file);
      this.selectedFilePreviewUrl.set(previewUrl);

      onCleanup(() => {
        URL.revokeObjectURL(previewUrl);
      });
    });
  }

  protected async onUpload(): Promise<void> {
    const file = this.selectedFile();
    if (!file || this.isUploading()) {
      return;
    }

    await this.uploadFacadeService.uploadFile(file, (state) => {
      this.uploadState.set(state);
    });
  }

  protected setSelectedFile(file: File | null): void {
    this.selectedFile.set(file);
    this.uploadState.set(initialUploadState);
  }
}
