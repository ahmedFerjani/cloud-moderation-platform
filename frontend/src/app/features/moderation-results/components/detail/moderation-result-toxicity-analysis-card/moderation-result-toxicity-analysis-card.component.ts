import { Component, computed, input } from '@angular/core';
import { MatChipsModule } from '@angular/material/chips';
import { PropertyRowComponent } from '../../../../../shared/components/property-row/property-row.component';
import { ModerationResultDetailCardShellComponent } from '../moderation-result-detail-card-shell/moderation-result-detail-card-shell.component';
import type { TextInsights } from '../../../models/moderation-results.model';

@Component({
  selector: 'app-moderation-result-toxicity-analysis-card',
  imports: [MatChipsModule, ModerationResultDetailCardShellComponent, PropertyRowComponent],
  templateUrl: './moderation-result-toxicity-analysis-card.component.html',
  styleUrl: './moderation-result-toxicity-analysis-card.component.scss',
})
export class ModerationResultToxicityAnalysisCardComponent {
  readonly insights = input<TextInsights | null>(null);
  readonly detectionThreshold = input<number>(0.7);

  readonly orderedLabels = computed(() => {
    const labels = this.insights()?.toxicity_labels ?? [];
    return [...labels].sort((left, right) => right.score - left.score);
  });

  protected formatScorePercent(score: number | null | undefined): string {
    if (score === null || score === undefined) {
      return '-';
    }

    return `${(score * 100).toFixed(1)}%`;
  }

  protected formatPiiTypes(piiEntityTypes: string[]): string {
    if (piiEntityTypes.length === 0) {
      return 'None';
    }

    return piiEntityTypes.join(', ');
  }
}
