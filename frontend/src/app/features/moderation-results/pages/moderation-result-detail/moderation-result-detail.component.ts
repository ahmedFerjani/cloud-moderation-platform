import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTreeModule } from '@angular/material/tree';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type { ModerationResultItem, TextInsights } from '../../models/moderation-results.model';
import type { OnInit } from '@angular/core';

interface SentimentScoreEntry {
  name: string;
  score: number;
}

interface ModerationLabelTreeNode {
  name: string;
  confidence: number | null;
  parentName: string | null;
  children: ModerationLabelTreeNode[];
}

type SentimentKey = 'positive' | 'neutral' | 'mixed' | 'negative';

@Component({
  selector: 'app-moderation-result-detail',
  imports: [
    DatePipe,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatTreeModule,
    RouterLink,
  ],
  templateUrl: './moderation-result-detail.component.html',
  styleUrl: './moderation-result-detail.component.scss',
})
export class ModerationResultDetailComponent implements OnInit {
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
  protected readonly moderationLabelChildrenAccessor = (node: ModerationLabelTreeNode) =>
    node.children;

  ngOnInit(): void {
    const imageId = this.route.snapshot.paramMap.get('imageId');
    this.imageId.set(imageId);

    if (!imageId) {
      this.errorMessage.set('Missing moderation result identifier.');
      this.isLoading.set(false);
      return;
    }

    void this.loadModerationResult(imageId);
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

  protected buildModerationLabelTree(item: ModerationResultItem): ModerationLabelTreeNode[] {
    const nodesByName = new Map<string, ModerationLabelTreeNode>();

    for (const label of item.moderation_labels) {
      nodesByName.set(label.Name, {
        name: label.Name,
        confidence: label.Confidence,
        parentName: label.ParentName || null,
        children: [],
      });
    }

    for (const node of nodesByName.values()) {
      if (!node.parentName) {
        continue;
      }

      let parentNode = nodesByName.get(node.parentName);
      if (!parentNode) {
        parentNode = {
          name: node.parentName,
          confidence: null,
          parentName: null,
          children: [],
        };
        nodesByName.set(node.parentName, parentNode);
      }

      parentNode.children.push(node);
    }

    const roots = [...nodesByName.values()].filter(
      (node) => !node.parentName || !nodesByName.has(node.parentName),
    );

    const sortNodes = (nodes: ModerationLabelTreeNode[]): void => {
      nodes.sort((left, right) => {
        const leftConfidence = left.confidence ?? -1;
        const rightConfidence = right.confidence ?? -1;
        if (leftConfidence !== rightConfidence) {
          return rightConfidence - leftConfidence;
        }

        return left.name.localeCompare(right.name);
      });

      for (const node of nodes) {
        if (node.children.length) {
          sortNodes(node.children);
        }
      }
    };

    sortNodes(roots);
    return roots;
  }

  protected formatConfidencePercent(confidence: number): string {
    return `${this.clampPercent(confidence).toFixed(1)}%`;
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
