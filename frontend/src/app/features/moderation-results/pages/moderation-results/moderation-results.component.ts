import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTreeModule } from '@angular/material/tree';
import { firstValueFrom } from 'rxjs';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type {
  ModerationResultItem,
  ModerationResultsResponse,
  TextInsights,
} from '../../models/moderation-results.model';
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
  selector: 'app-moderation-results',
  imports: [
    DatePipe,
    FormsModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTreeModule,
  ],
  templateUrl: './moderation-results.component.html',
  styleUrl: './moderation-results.component.scss',
})
export class ModerationResultsComponent implements OnInit {
  private readonly moderationResultsApiService = inject(ModerationResultsApiService);
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

  protected readonly selectedStatuses = signal<('safe' | 'unsafe')[]>(['safe', 'unsafe']);
  protected readonly limit = signal(1);
  protected readonly limitOptions = [1, 2] as const;
  protected readonly isLoading = signal(true);
  protected readonly isLoadingMore = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly items = signal<ModerationResultItem[]>([]);
  protected readonly count = signal(0);
  protected readonly lastEvaluatedKey = signal<Record<string, string> | null>(null);
  protected readonly hasItems = computed(() => this.items().length > 0);
  protected readonly filteredItems = computed(() => {
    const selectedStatuses = this.selectedStatuses();
    if (selectedStatuses.length === 0 || selectedStatuses.length === 2) {
      return this.items();
    }

    const includeSafe = selectedStatuses.includes('safe');
    const includeUnsafe = selectedStatuses.includes('unsafe');

    return this.items().filter((item) => (item.unsafe_detected ? includeUnsafe : includeSafe));
  });
  protected readonly hasFilteredItems = computed(() => this.filteredItems().length > 0);
  protected readonly hasMore = computed(() => this.lastEvaluatedKey() !== null);
  protected readonly moderationLabelChildrenAccessor = (node: ModerationLabelTreeNode) =>
    node.children;

  ngOnInit(): void {
    void this.loadModerationResults();
  }

  protected onLimitChange(value: number): void {
    this.limit.set(value);
    void this.loadModerationResults();
  }

  protected async loadModerationResults(): Promise<void> {
    await this.fetchResults('replace');
  }

  protected async loadMore(): Promise<void> {
    await this.fetchResults('append');
  }

  protected toggleStatus(status: 'safe' | 'unsafe'): void {
    const current = this.selectedStatuses();
    if (current.includes(status)) {
      this.selectedStatuses.set(current.filter((itemStatus) => itemStatus !== status));
      return;
    }

    this.selectedStatuses.set([...current, status]);
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

  private async fetchResults(mode: 'replace' | 'append'): Promise<void> {
    const isAppendMode = mode === 'append';

    if (isAppendMode) {
      this.isLoadingMore.set(true);
    } else {
      this.isLoading.set(true);
      this.errorMessage.set(null);
      this.lastEvaluatedKey.set(null);
    }

    try {
      const response = await firstValueFrom<ModerationResultsResponse>(
        this.moderationResultsApiService.getModerationResults(
          this.limit(),
          isAppendMode ? this.lastEvaluatedKey() : undefined,
        ),
      );
      if (isAppendMode) {
        this.count.update((current) => current + response.count);
      } else {
        this.count.set(response.count);
      }
      this.lastEvaluatedKey.set(response.last_evaluated_key);

      const mappedItems = this.mapItems(response.items);
      if (isAppendMode) {
        this.items.update((current) => [...current, ...mappedItems]);
      } else {
        this.items.set(mappedItems);
      }
    } catch {
      if (isAppendMode) {
        this.errorMessage.set('Unable to load more results. Please try again.');
      } else {
        this.errorMessage.set('Unable to load moderation results right now. Please try again.');
        this.items.set([]);
        this.count.set(0);
      }
    } finally {
      if (isAppendMode) {
        this.isLoadingMore.set(false);
      } else {
        this.isLoading.set(false);
      }
    }
  }

  private mapItems(items: ModerationResultItem[]): ModerationResultItem[] {
    return items.map((item) => ({
      ...item,
      moderation_labels: item.moderation_labels.slice(0, 5),
    }));
  }
}
