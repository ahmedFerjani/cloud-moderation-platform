import { DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { ModerationResultDetailCardShellComponent } from '../moderation-result-detail-card-shell/moderation-result-detail-card-shell.component';
import { ModerationResultInfoRowComponent } from '../moderation-result-info-row/moderation-result-info-row.component';
import type { ModerationResultItem } from '../../../models/moderation-results.model';

@Component({
  selector: 'app-moderation-result-general-info-card',
  imports: [DatePipe, ModerationResultDetailCardShellComponent, ModerationResultInfoRowComponent],
  templateUrl: './moderation-result-general-info-card.component.html',
  styleUrl: './moderation-result-general-info-card.component.scss',
})
export class ModerationResultGeneralInfoCardComponent {
  readonly item = input.required<ModerationResultItem>();
}
