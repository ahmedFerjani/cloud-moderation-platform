import { Component, computed, input } from '@angular/core';
import { ModerationResultDetailCardShellComponent } from '../moderation-result-detail-card-shell/moderation-result-detail-card-shell.component';
import { ModerationResultInfoRowComponent } from '../moderation-result-info-row/moderation-result-info-row.component';
import type { TextInsights } from '../../../models/moderation-results.model';

interface SentimentScoreEntry {
  name: string;
  score: number;
}

@Component({
  selector: 'app-moderation-result-sentiment-analysis-card',
  imports: [ModerationResultDetailCardShellComponent, ModerationResultInfoRowComponent],
  templateUrl: './moderation-result-sentiment-analysis-card.component.html',
  styleUrl: './moderation-result-sentiment-analysis-card.component.scss',
})
export class ModerationResultSentimentAnalysisCardComponent {
  readonly insights = input<TextInsights | null>(null);

  readonly fixedScores = computed<SentimentScoreEntry[]>(() => {
    const scores = this.insights()?.sentiment_scores;
    if (!scores) {
      return [];
    }

    return [
      { name: 'Positive', score: scores.Positive },
      { name: 'Neutral', score: scores.Neutral },
      { name: 'Mixed', score: scores.Mixed },
      { name: 'Negative', score: scores.Negative },
    ];
  });

  protected formatScorePercent(score: number | null | undefined): string {
    if (score === null || score === undefined) {
      return '-';
    }

    return `${(score * 100).toFixed(1)}%`;
  }
}
