import { Component, computed, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-upload-page',
  imports: [MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './upload-page.component.html',
  styleUrl: './upload-page.component.scss',
})
export class UploadPageComponent {
  protected readonly isDragActive = signal(false);
  protected readonly selectedFileName = signal<string | null>(null);
  protected readonly selectedFileSizeBytes = signal<number | null>(null);
  protected readonly selectedFilePreviewUrl = signal<string | null>(null);
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

  protected onUpload(): void {
    // Backend integration comes in the next increment.
  }

  private setSelectedFile(file: File | null): void {
    const currentPreviewUrl = this.selectedFilePreviewUrl();
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }

    this.selectedFileName.set(file?.name ?? null);
    this.selectedFileSizeBytes.set(file?.size ?? null);
    this.selectedFilePreviewUrl.set(file ? URL.createObjectURL(file) : null);
  }
}
