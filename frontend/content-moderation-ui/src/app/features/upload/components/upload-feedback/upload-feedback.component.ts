import { Component, computed, input } from '@angular/core';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { UploadState } from '../../models/upload-state.model';

@Component({
  selector: 'app-upload-feedback',
  imports: [MatProgressBarModule],
  templateUrl: './upload-feedback.component.html',
  styleUrl: './upload-feedback.component.scss',
})
export class UploadFeedbackComponent {
  readonly uploadState = input.required<UploadState>();

  protected readonly isUploading = computed(() => {
    const phase = this.uploadState().phase;
    return phase === 'requestingUrl' || phase === 'uploading';
  });
}
