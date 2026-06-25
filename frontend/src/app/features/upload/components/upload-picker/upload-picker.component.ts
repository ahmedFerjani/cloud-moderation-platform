import { Component, input, output, signal, ChangeDetectionStrategy } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-upload-picker',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './upload-picker.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './upload-picker.component.scss',
})
export class UploadPickerComponent {
  readonly acceptedFormats = input('image/jpeg,image/png');
  readonly disabled = input(false);
  readonly maxFiles = input(10);
  readonly describedBy = input<string | null>(null);

  readonly filesSelected = output<File[]>();

  protected readonly isDragActive = signal(false);

  protected onFileInputChange(event: Event): void {
    const inputElement = event.target as HTMLInputElement;
    const files = this.pickFiles(inputElement.files);
    this.filesSelected.emit(files);
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
    const files = this.pickFiles(event.dataTransfer?.files);
    this.filesSelected.emit(files);
  }

  private pickFiles(fileList: FileList | null | undefined): File[] {
    if (!fileList) {
      return [];
    }

    return Array.from(fileList).slice(0, this.maxFiles());
  }
}
