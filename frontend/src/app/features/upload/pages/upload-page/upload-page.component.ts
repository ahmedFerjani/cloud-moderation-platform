import {
  Component,
  computed,
  effect,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { SelectedFilePreviewComponent } from '../../components/selected-file-preview/selected-file-preview.component';
import { UploadFeedbackComponent } from '../../components/upload-feedback/upload-feedback.component';
import { UploadPickerComponent } from '../../components/upload-picker/upload-picker.component';
import { UploadFacadeService } from '../../facades/upload-facade.service';
import { initialUploadState } from '../../models/upload-state.model';
import type { UploadState } from '../../models/upload-state.model';

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
  changeDetection: ChangeDetectionStrategy.Eager,
  templateUrl: './upload-page.component.html',
})
export class UploadPageComponent {
  private readonly uploadFacadeService = inject(UploadFacadeService);

  protected readonly selectedFiles = signal<File[]>([]);
  protected readonly selectedFilePreviewUrls = signal<string[]>([]);
  protected readonly selectedFilesCount = computed(() => this.selectedFiles().length);
  protected readonly selectedFilesTotalSizeLabel = computed(() => {
    const totalSize = this.selectedFiles().reduce((acc, file) => acc + file.size, 0);
    return totalSize > 0 ? this.formatFileSize(totalSize) : null;
  });
  protected readonly uploadState = signal<UploadState>(initialUploadState);
  protected readonly isUploading = computed(() => {
    const phase = this.uploadState().phase;
    return phase === 'requestingUrl' || phase === 'uploading';
  });

  constructor() {
    effect((onCleanup) => {
      const files = this.selectedFiles();
      if (files.length === 0) {
        this.selectedFilePreviewUrls.set([]);
        return;
      }

      const previewUrls = files.map((file) => URL.createObjectURL(file));
      this.selectedFilePreviewUrls.set(previewUrls);

      onCleanup(() => {
        for (const previewUrl of previewUrls) {
          URL.revokeObjectURL(previewUrl);
        }
      });
    });
  }

  protected async onUpload(): Promise<void> {
    const files = this.selectedFiles();
    if (files.length === 0 || this.isUploading()) {
      return;
    }

    await this.uploadFacadeService.uploadFiles(files, (state) => {
      this.uploadState.set(state);
    });
  }

  protected setSelectedFiles(files: File[]): void {
    this.selectedFiles.set(files);
    this.uploadState.set(initialUploadState);
  }

  protected removeSelectedFile(index: number): void {
    const nextFiles = this.selectedFiles().filter((_, currentIndex) => currentIndex !== index);
    this.selectedFiles.set(nextFiles);
    this.uploadState.set(initialUploadState);
  }

  protected filePreviewUrl(index: number): string | null {
    return this.selectedFilePreviewUrls()[index] ?? null;
  }

  protected formatFileSize(size: number): string {
    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }
}
