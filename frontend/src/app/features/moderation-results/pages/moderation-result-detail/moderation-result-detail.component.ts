import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { ModerationResultGeneralInfoCardComponent } from '../../components/detail/moderation-result-general-info-card/moderation-result-general-info-card.component';
import { ModerationResultImageAccessCardComponent } from '../../components/detail/moderation-result-image-access-card/moderation-result-image-access-card.component';
import { ModerationResultLabelAnalysisCardComponent } from '../../components/detail/moderation-result-label-analysis-card/moderation-result-label-analysis-card.component';
import { ModerationResultSentimentAnalysisCardComponent } from '../../components/detail/moderation-result-sentiment-analysis-card/moderation-result-sentiment-analysis-card.component';
import { ModerationResultSummaryCardComponent } from '../../components/detail/moderation-result-summary-card/moderation-result-summary-card.component';
import { ModerationResultToxicityAnalysisCardComponent } from '../../components/detail/moderation-result-toxicity-analysis-card/moderation-result-toxicity-analysis-card.component';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type {
  ModerationResultItem,
  TextInsights,
  ViewAccess,
} from '../../models/moderation-results.model';
import type { OnDestroy, OnInit } from '@angular/core';

interface SentimentScoreEntry {
  name: string;
  score: number;
}

type SentimentKey = 'positive' | 'neutral' | 'mixed' | 'negative';

@Component({
  selector: 'app-moderation-result-detail',
  imports: [
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    ModerationResultGeneralInfoCardComponent,
    ModerationResultImageAccessCardComponent,
    ModerationResultLabelAnalysisCardComponent,
    ModerationResultSentimentAnalysisCardComponent,
    ModerationResultSummaryCardComponent,
    ModerationResultToxicityAnalysisCardComponent,
    RouterLink,
  ],
  templateUrl: './moderation-result-detail.component.html',
  styleUrl: './moderation-result-detail.component.scss',
})
export class ModerationResultDetailComponent implements OnInit, OnDestroy {
  protected readonly toxicityDetectionThreshold = 0.7;
  private readonly moderationResultsApiService = inject(ModerationResultsApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly sentimentIconMap: Record<SentimentKey, string> = {
    positive: 'sentiment_satisfied',
    neutral: 'sentiment_neutral',
    mixed: 'sentiment_satisfied_alt',
    negative: 'sentiment_dissatisfied',
  };
  private readonly sentimentToneClassMap: Record<SentimentKey, string> = {
    positive: 'overview-icon--positive',
    neutral: 'overview-icon--neutral',
    mixed: 'overview-icon--mixed',
    negative: 'overview-icon--negative',
  };

  protected readonly imageId = signal<string | null>(null);
  protected readonly item = signal<ModerationResultItem | null>(null);
  protected readonly isLoading = signal(true);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly hasItem = computed(() => this.item() !== null);
  protected readonly nowMs = signal(Date.now());
  protected readonly isRefreshingViewAccess = signal(false);
  protected readonly viewAccessErrorMessage = signal<string | null>(null);
  protected readonly currentViewAccess = computed(() => this.item()?.view_access ?? null);
  protected readonly viewAccessRemainingSeconds = computed(() => {
    const access = this.currentViewAccess();
    if (!access) {
      return null;
    }

    const issuedAtMs = Date.parse(access.issued_at);
    if (Number.isNaN(issuedAtMs)) {
      return null;
    }

    const expiresAtMs = issuedAtMs + access.expires_in * 1000;
    return Math.max(0, Math.floor((expiresAtMs - this.nowMs()) / 1000));
  });
  protected readonly isViewAccessActive = computed(() => {
    const remaining = this.viewAccessRemainingSeconds();
    return remaining !== null && remaining > 0;
  });
  private tickIntervalId: number | null = null;

  ngOnInit(): void {
    this.tickIntervalId = window.setInterval(() => {
      this.nowMs.set(Date.now());
    }, 1000);

    const imageId = this.route.snapshot.paramMap.get('imageId');
    this.imageId.set(imageId);

    if (!imageId) {
      this.errorMessage.set('Missing moderation result identifier.');
      this.isLoading.set(false);
      return;
    }

    void this.loadModerationResult(imageId);
  }

  ngOnDestroy(): void {
    if (this.tickIntervalId !== null) {
      window.clearInterval(this.tickIntervalId);
      this.tickIntervalId = null;
    }
  }

  protected async refresh(): Promise<void> {
    const imageId = this.imageId();
    if (!imageId) {
      return;
    }

    await this.loadModerationResult(imageId);
  }

  protected getTextInsights(item: ModerationResultItem): TextInsights | null {
    const insights = item.text_insights;
    return insights && insights.analyzed_text_length > 0 ? insights : null;
  }

  protected getSentimentIcon(sentiment: string): string {
    return this.sentimentIconMap[this.normalizeSentiment(sentiment)];
  }

  protected getSentimentToneClass(sentiment: string): string {
    return this.sentimentToneClassMap[this.normalizeSentiment(sentiment)];
  }

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

  protected getFixedSentimentScores(insights: TextInsights): SentimentScoreEntry[] {
    const { sentiment_scores: scores } = insights;
    return [
      { name: 'Positive', score: scores.Positive },
      { name: 'Neutral', score: scores.Neutral },
      { name: 'Mixed', score: scores.Mixed },
      { name: 'Negative', score: scores.Negative },
    ];
  }

  protected getOrderedToxicityLabels(insights: TextInsights): TextInsights['toxicity_labels'] {
    return [...insights.toxicity_labels].sort((left, right) => right.score - left.score);
  }

  protected formatRemainingTime(totalSeconds: number | null): string {
    if (totalSeconds === null) {
      return 'Unavailable';
    }

    const minutes = Math.floor(totalSeconds / 60)
      .toString()
      .padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  protected async renewViewUrl(): Promise<void> {
    const imageId = this.imageId();
    if (!imageId || this.isRefreshingViewAccess()) {
      return;
    }

    this.isRefreshingViewAccess.set(true);
    this.viewAccessErrorMessage.set(null);

    try {
      const response = await firstValueFrom(
        this.moderationResultsApiService.getModerationResultViewAccess(imageId),
      );

      const currentItem = this.item();
      if (!currentItem) {
        return;
      }

      this.item.set({
        ...currentItem,
        view_access: response.view_access,
      });
      this.nowMs.set(Date.now());
    } catch {
      this.viewAccessErrorMessage.set('Unable to renew image URL right now. Please try again.');
    } finally {
      this.isRefreshingViewAccess.set(false);
    }
  }

  protected getViewAccessStatusLabel(viewAccess: ViewAccess | null): string {
    if (!viewAccess) {
      return 'Unavailable';
    }

    return this.isViewAccessActive() ? 'Active' : 'Expired';
  }

  private async loadModerationResult(imageId: string): Promise<void> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    try {
      const item = await firstValueFrom(
        this.moderationResultsApiService.getModerationResult(imageId),
      );
      this.item.set(item);
    } catch {
      this.errorMessage.set('Unable to load moderation result right now. Please try again.');
      this.item.set(null);
    } finally {
      this.isLoading.set(false);
    }
  }

  private normalizeSentiment(sentiment: string): SentimentKey {
    const normalized = sentiment.trim().toLowerCase();
    if (normalized === 'positive') {
      return 'positive';
    }
    if (normalized === 'negative') {
      return 'negative';
    }
    if (normalized === 'mixed') {
      return 'mixed';
    }

    return 'neutral';
  }

  private clampPercent(value: number): number {
    return Math.max(0, Math.min(value, 100));
  }
}
