import { Component, computed, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

export type SummaryCardTone = 'success' | 'warning' | 'neutral';

@Component({
  selector: 'app-moderation-result-summary-card',
  imports: [MatIconModule],
  templateUrl: './moderation-result-summary-card.component.html',
  styleUrl: './moderation-result-summary-card.component.scss',
})
export class ModerationResultSummaryCardComponent {
  readonly label = input.required<string>();
  readonly value = input.required<string>();
  readonly icon = input.required<string>();
  readonly tone = input<SummaryCardTone>('neutral');

  readonly toneClass = computed(() => {
    switch (this.tone()) {
      case 'success':
        return 'overview-icon--safe';
      case 'warning':
        return 'overview-icon--toxic';
      default:
        return 'overview-icon--neutral';
    }
  });
}
