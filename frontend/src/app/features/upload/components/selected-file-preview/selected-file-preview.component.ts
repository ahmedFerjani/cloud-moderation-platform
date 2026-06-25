import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-selected-file-preview',
  imports: [MatButtonModule],
  templateUrl: './selected-file-preview.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './selected-file-preview.component.scss',
})
export class SelectedFilePreviewComponent {
  readonly fileName = input.required<string>();
  readonly sizeLabel = input<string | null>(null);
  readonly previewUrl = input<string | null>(null);

  readonly removeRequested = output<void>();

  protected onRemoveRequested(): void {
    this.removeRequested.emit();
  }
}
