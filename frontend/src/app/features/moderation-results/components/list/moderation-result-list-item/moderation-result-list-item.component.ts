import { DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import type { ModerationResultItem, TextInsights } from '../../../models/moderation-results.model';

@Component({
  selector: 'app-moderation-result-list-item',
  imports: [DatePipe, MatButtonModule, MatIconModule, RouterLink],
  templateUrl: './moderation-result-list-item.component.html',
  styleUrl: './moderation-result-list-item.component.scss',
})
export class ModerationResultListItemComponent {
  readonly item = input.required<ModerationResultItem>();

  protected getTextInsights(item: ModerationResultItem): TextInsights | null {
    const insights = item.text_insights;
    return insights && insights.analyzed_text_length > 0 ? insights : null;
  }

  protected getTopModerationLabel(item: ModerationResultItem): string | null {
    return item.moderation_labels[0]?.Name ?? null;
  }

  protected getSummaryS3Path(item: ModerationResultItem): string {
    return item.s3_key;
  }
}
