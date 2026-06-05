import { Component, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-upload-picker',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './upload-picker.component.html',
  styleUrl: './upload-picker.component.scss',
})
export class UploadPickerComponent {
  readonly acceptedFormats = input('image/jpeg,image/png');
  readonly disabled = input(false);
  readonly describedBy = input<string | null>(null);

  readonly fileSelected = output<File | null>();

  protected readonly isDragActive = signal(false);

  protected onFileInputChange(event: Event): void {
    const inputElement = event.target as HTMLInputElement;
    const file = inputElement.files?.[0] ?? null;
    this.fileSelected.emit(file);
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
    const file = event.dataTransfer?.files[0] ?? null;
    this.fileSelected.emit(file);
  }
}
